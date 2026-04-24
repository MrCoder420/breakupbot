# Eleanor Mind — Breakup Recovery & Emotional Support Bot
## Project Detailed Report

### 1. Overview
**Eleanor Mind** is a production-ready, RAG-enabled (Retrieval-Augmented Generation) emotional support chatbot. It is specifically designed to provide therapeutic guidance and empathetic companionship for people going through breakups and relationship heartbreaks.

The system combines the warmth of a "best friend" persona with the clinical knowledge of a therapist, rooted in evidence-based strategies like CBT (Cognitive Behavioral Therapy) and DBT (Dialectical Behavior Therapy).

---

### 2. Technical Stack
The project is built using a modern, scalable AI stack:

- **Frontend:** React (TypeScript) + Vite
  - Custom glassmorphism UI with a focus on deep aesthetics and responsive design.
  - Lucide-React for modern iconography.
- **Backend:** FastAPI (Python)
  - Managed via Uvicorn.
  - Asynchronous endpoints for high-performance handling of requests.
- **AI Core:** LangChain
  - **LLM:** Groq (Llama-3.1-8b-instant) for low-latency, high-quality responses.
  - **Memory:** Recursive history management integrated with MongoDB.
- **RAG Engine (Knowledge Retrieval):**
  - **Vector Database:** ChromaDB (Local storage).
  - **Embeddings:** Hugging Face Inference API (serverless) using `sentence-transformers/all-MiniLM-L6-v2`.
- **Database:** MongoDB Atlas
  - Stores persistent user data and encrypted chat histories.
- **Security:** JWT (JSON Web Tokens)
  - Secure authentication (Register/Login) with passwords hashed via `bcrypt`.

---

### 3. Core Features

#### 🧠 RAG (Retrieval-Augmented Generation)
Unlike generic chatbots, Eleanor Mind "reads" from a high-quality mental health knowledge base before answering. 
- **Knowledge Base:** Over 5,000 curated chunks of professional mental health counseling conversations and relationship advice.
- **Top-K Retrieval:** The bot fetches the top 4 most relevant entries from ChromaDB for every message to ensure advice is grounded in clinical wisdom.

#### 🔐 User Authentication & Privacy
- **Isolated -Histories:** Each user must register and log in. 
- **Encryption:** Chat histories are locked to specific user IDs in MongoDB. A user's conversation is completely private and never visible to others.

#### 💬 Persistent Conversational Memory
The bot remembers everything you say. Even if you refresh the page or clear your cache, your past conversations are restored instantly from MongoDB.

#### 📱 Responsive Design
The UI is fully optimized for both Desktop and Mobile, featuring:
- Smooth transitions.
- Interactive typing indicators.
- Tailored bubble widths for mobile reading.

---

### 4. How the "Brain" Works (System Architecture)
1. **User Input:** User sends a message via the React UI.
2. **Authentication:** Backend verifies the JWT token.
3. **Retrieval (RAG):** The system converts the user's input into a math vector and searches the **ChromaDB** for similar counseling data.
4. **Context Building:** The retrieved advice + the user's chat history + the user's current message are bundled together.
5. **LLM Generation:** This bundle is sent to **Groq**. Groq generates a warm, short, empathetic response.
6. **Persistence:** The new response is saved back to **MongoDB** and sent to the User.

---

### 5. Hosting & Deployment
- **Frontend:** Hosted on **Vercel** for lightning-fast global delivery.
- **Backend:** Hosted on **Render** (Web Service).
- **Architecture Strategy:** "Split Hosting" was used to avoid memory limits and ensure persistent access to the RAG database while keeping the UI fast.

---

### 6. Local Setup Instructions
To run this project locally:
1. `pip install -r requirements.txt`
2. Create a `.env` file with `GROQ_API_KEY`, `MONGO_URI`, and `HF_TOKEN`.
3. `python -m uvicorn app:app --reload`
4. `cd frontend && npm install && npm run dev`

---

### 7. Final Status
The project is **completed and fully operational**. It successfully bridges the gap between high-tech AI and warm, human-centric emotional support.
