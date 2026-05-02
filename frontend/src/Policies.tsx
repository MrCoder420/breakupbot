import React from 'react';
import { X } from 'lucide-react';

type PolicyModalProps = {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

const PolicyModal = ({ title, isOpen, onClose, children }: PolicyModalProps) => {
  if (!isOpen) return null;
  return (
    <div className="modal-overlay" style={{ zIndex: 2000 }}>
      <div className="paywall-card" style={{ maxWidth: '600px', textAlign: 'left', maxHeight: '80vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '1.5rem' }}>{title}</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#a497bd', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>
        <div style={{ color: '#e5dcf2', lineHeight: '1.6', fontSize: '0.9rem' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default function Policies() {
  const [modal, setModal] = React.useState<string | null>(null);

  const policies = {
    contact: (
      <>
        <h3>Contact Us</h3>
        <p>If you have any questions about these Terms, please contact us:</p>
        <ul>
          <li>By email: support@mrcoder420.me</li>
          <li>By visiting this page on our website: https://breakupbot.mrcoder420.me</li>
          <li>Phone: +91 9876543210</li>
          <li>Address: Pune, Maharashtra, India</li>
        </ul>
      </>
    ),
    terms: (
      <>
        <h3>Terms & Conditions</h3>
        <p>Last updated: May 02, 2026</p>
        <p>Welcome to Breakup Bot. By using our service, you agree to these terms.</p>
        <p>1. Service: We provide an AI-driven emotional support chatbot.</p>
        <p>2. Subscriptions: We offer a monthly subscription for ₹1. Payments are processed via Razorpay.</p>
        <p>3. Use: You must not use the bot for any illegal purposes.</p>
      </>
    ),
    privacy: (
      <>
        <h3>Privacy Policy</h3>
        <p>Last updated: May 02, 2026</p>
        <p>Your privacy is important to us. We only collect your username and chat history to provide the service.</p>
        <p>1. Data: We store your chat history securely in MongoDB.</p>
        <p>2. Security: We use industry-standard encryption to protect your data.</p>
      </>
    ),
    refund: (
      <>
        <h3>Refund & Cancellation Policy</h3>
        <p>Last updated: May 02, 2026</p>
        <p>1. Subscription: The ₹1 subscription is valid for 30 days.</p>
        <p>2. Refunds: Since this is a digital service with an immediate activation, refunds are generally not provided. However, if you experience technical issues, contact us within 24 hours.</p>
        <p>3. Cancellation: You can cancel your subscription at any time, but no partial refunds will be issued.</p>
      </>
    )
  };

  return (
    <>
      <div style={{ 
        marginTop: '30px', 
        display: 'flex', 
        gap: '15px', 
        fontSize: '0.75rem', 
        color: '#a497bd',
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        <span onClick={() => setModal('contact')} style={{ cursor: 'pointer', textDecoration: 'underline' }}>Contact</span>
        <span onClick={() => setModal('terms')} style={{ cursor: 'pointer', textDecoration: 'underline' }}>Terms</span>
        <span onClick={() => setModal('privacy')} style={{ cursor: 'pointer', textDecoration: 'underline' }}>Privacy</span>
        <span onClick={() => setModal('refund')} style={{ cursor: 'pointer', textDecoration: 'underline' }}>Refunds</span>
      </div>

      <PolicyModal title="Contact Details" isOpen={modal === 'contact'} onClose={() => setModal(null)}>
        {policies.contact}
      </PolicyModal>
      <PolicyModal title="Terms & Conditions" isOpen={modal === 'terms'} onClose={() => setModal(null)}>
        {policies.terms}
      </PolicyModal>
      <PolicyModal title="Privacy Policy" isOpen={modal === 'privacy'} onClose={() => setModal(null)}>
        {policies.privacy}
      </PolicyModal>
      <PolicyModal title="Refund Policy" isOpen={modal === 'refund'} onClose={() => setModal(null)}>
        {policies.refund}
      </PolicyModal>
    </>
  );
}
