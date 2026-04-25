import os
import json
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from pymongo import MongoClient
import certifi

# Remote embeddings from HuggingFace (Production Mode - Required for Render)
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from personality import get_chat_prompt

load_dotenv()

# ── Env ──────────────────────────────────────────────────────────────────────
MONGO_URI    = os.getenv("MONGO_URI", "mongodb://localhost:27017")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN     = os.getenv("HF_TOKEN", "")
if HF_TOKEN:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

# JWT Config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "b9d28a3f890e4f8d951f08bd9ea6b1bb348a47ce0c7bb0bffe4a4ab5fc321cf")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Breakup Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ── Schemas ───────────────────────────────────────────────────────────────────
class UserAuth(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    # session_id is no longer provided by frontend. We infer it from the logged-in user.

# ── Init DB Connections ───────────────────────────────────────────────────────
print("Loading Chroma vector store from ./chroma_db ...")
print("Connecting to HuggingFace Inference API for embeddings...")
embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=HF_TOKEN,
    model="BAAI/bge-small-en-v1.5"
)

# Health Check for Render
@app.get("/")
@app.head("/")
async def root():
    return {
        "status": "online", 
        "bot": "Eleanor Mind", 
        "env_check": {
            "GROQ": "SET" if GROQ_API_KEY else "MISSING",
            "MONGO": "SET" if os.getenv("MONGO_URI") else "MISSING",
            "HF": "SET" if HF_TOKEN else "MISSING",
            "JWT": "SET" if os.getenv("JWT_SECRET_KEY") else "MISSING"
        }
    }

try:
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )
    doc_count = vectorstore._collection.count()
    print(f"Chroma loaded OK — {doc_count} vectors ready.")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})  # k=4 for richer context
except Exception as e:
    print(f"WARNING: Chroma load failed — RAG disabled. Error: {e}")
    retriever = None


mongo_client = (
    MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    if MONGO_URI.startswith("mongodb+srv")
    else MongoClient(MONGO_URI)
)
db = mongo_client.breakup_bot_db
users_collection = db.users

# ── Auth Utilities ────────────────────────────────────────────────────────────

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return username


# ── Auth Endpoints ────────────────────────────────────────────────────────────

@app.post("/register")
async def register(auth: UserAuth):
    try:
        if users_collection.find_one({"username": auth.username}):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = get_password_hash(auth.password)
        users_collection.insert_one({
            "username": auth.username,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        })
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"REGISTRATION ERROR: {e}")
        return {"error_debug": str(e), "tip": "Check MongoDB IP Whitelist (0.0.0.0/0)"}


@app.post("/login")
async def login(user: UserAuth):
    try:
        db_user = users_collection.find_one({"username": user.username})
        if not db_user:
            raise HTTPException(status_code=401, detail="User not found")
            
        if not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect password")
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "username": user.username}
    except Exception as e:
        print(f"LOGIN ERROR: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Auth Error: {str(e)}")


# ── Init LLM ──────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    api_key=GROQ_API_KEY,
)


# ── Chat Setup & Endpoints ────────────────────────────────────────────────────

def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=None,
        client=mongo_client,
        database_name="breakup_bot_db",
        collection_name="chat_histories",
    )

prompt = get_chat_prompt()

def get_context(query: str) -> str:
    if retriever is None:
        return "No knowledge base available."
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant context found."
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

chain = (
    {
        "context":      lambda x: get_context(x["input"]),
        "input":        lambda x: x["input"],
        "chat_history": lambda x: x.get("chat_history", []),
    }
    | prompt
    | llm
    | StrOutputParser()
)

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


@app.post("/chat")
async def chat_endpoint(req: ChatRequest, current_user: str = Depends(get_current_user)):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in .env")

    try:
        # The user's individual chat history is keyed purely off their authenticated username
        response = chain_with_history.invoke(
            {"input": req.message},
            config={"configurable": {"session_id": current_user}},
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(current_user: str = Depends(get_current_user)):
    try:
        # Fetching history uses the identical username-based session ID
        history = get_session_history(current_user)
        messages = []
        for msg in history.messages:
            role = "user" if msg.type == "human" else "bot"
            messages.append({"role": role, "content": msg.content})
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    chroma_docs = vectorstore._collection.count() if retriever else 0
    return {
        "status": "Breakup Bot API is online",
        "rag_vectors": chroma_docs,
        "groq_model": "llama-3.1-8b-instant",
        "mongo": "connected",
        "auth": "enabled"
    }
