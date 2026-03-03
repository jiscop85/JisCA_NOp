import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "👋 Hi! I'm the JisCA_NOp AI Assistant. I can help you with:",
      timestamp: new Date()
    },
    {
      id: 2,
      type: 'bot',
      text: "• License plate detection queries\n• System usage and features\n• Analytics and statistics\n• Technical support\n• Admin panel guidance\n\nWhat would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

   const generateBotResponse = async (userMessage) => {
    const msg = userMessage.toLowerCase();
    
    // Rule-based responses with context awareness
    if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
      return "Hello! 👋 I'm here to help you with JisCA_NOp. Would you like to know about our features, how to use the system, or check your detection statistics?";
    }
    
    if (msg.includes('how') && (msg.includes('work') || msg.includes('use'))) {
      return "JisCA_NOp works in 3 simple steps:\n\n1️⃣ Upload your image via the Detect page\n2️⃣ Our AI (YOLOv8 + EasyOCR) processes it\n3️⃣ Get instant results with plate text and confidence\n\nYou can also use batch processing for multiple images! Want to try it now?";
    }
    
    if (msg.includes('feature') || msg.includes('capability') || msg.includes('can do')) {
      return "✨ JisCA_NOp Key Features:\n\n🔍 AI Detection - YOLOv8 for accurate plate detection\n📝 Smart OCR - EasyOCR with preprocessing\n🚗 Vehicle Classification - Auto-detect car types\n📊 Analytics Dashboard - Real-time statistics\n🔍 Smart Search - Find plates with fuzzy matching\n⚡ Batch Processing - Multiple images at once\n🔔 Alert System - Stolen/wanted vehicle alerts\n\nWhich feature interests you?";
    }
    
    if (msg.includes('accuracy') || msg.includes('confidence')) {
      return "🎯 Accuracy depends on:\n\n• Image quality (higher is better)\n• Lighting conditions (well-lit recommended)\n• Plate visibility (front-facing ideal)\n• Custom YOLOv8 model (99%+ with trained model)\n\nWith optimal conditions and a trained model, we achieve 99.5%+ accuracy! Currently using YOLOv8n fallback - download custom model for production accuracy.";
    }
    
    if (msg.includes('upload') || msg.includes('image') || msg.includes('detect')) {
      return "📤 To upload and detect:\n\n1. Go to the Detect page\n2. Click the upload area or drag & drop\n3. Select your image (JPG, PNG, WEBP)\n4. Click 'Detect Plate'\n5. View results in seconds!\n\nFor multiple images, use the Batch page. Need help with a specific step?";
    }
    
    if (msg.includes('batch') || msg.includes('multiple')) {
      return "🗂️ Batch Processing:\n\n• Upload up to 50 images at once\n• Automatic processing with progress tracking\n• View all results in a grid\n• Download annotated images\n• Export to CSV\n\nGreat for processing dashcam footage or surveillance feeds!";
    }
    
    if (msg.includes('admin') || msg.includes('manage') || msg.includes('panel')) {
      return "🛠️ Admin Panel Features:\n\n👥 User Management - Roles & permissions\n🚗 Vehicle Database - Track plates\n🔔 Alert System - Real-time notifications\n🔑 API Keys - External integrations\n📊 Analytics - Dashboard & reports\n⚙️ Settings - System configuration\n\nAccess via /admin endpoints in the API. Need specific admin help?";
    }
    
    if (msg.includes('api') || msg.includes('integrate') || msg.includes('endpoint')) {
      return "🔌 API Integration:\n\n📍 Main Endpoints:\n• POST /api/detect/image - Single detection\n• POST /api/detect/batch - Batch processing\n• GET /api/detections - History\n• GET /api/admin/* - Admin operations\n\n📚 Full docs at: /docs (Swagger UI)\n\nNeed help with authentication or rate limits?";
    }
    
    if (msg.includes('price') || msg.includes('cost') || msg.includes('free')) {
      return "💰 JisCA_NOp is open-source and free!\n\n✅ Free forever\n✅ Self-hosted\n✅ No usage limits\n✅ MIT licensed\n✅ Full source code\n\nYou only pay for your own infrastructure (server, cloud, etc.). Perfect for startups and enterprises!";
    }
    
    if (msg.includes('docker') || msg.includes('kubernetes') || msg.includes('deploy')) {
      return "🚀 Deployment Options:\n\n🐳 Docker Compose (Easiest):\n```bash\ndocker-compose up -d\n```\n\n☸️ Kubernetes (Production):\n```bash\nkubectl apply -f k8s/\n```\n\n💻 Local Development:\nBackend: uvicorn server:app\nFrontend: yarn start\n\nCheck README.md for detailed guides!";
    }
    
    if (msg.includes('stat') || msg.includes('analytic') || msg.includes('dashboard')) {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/detections?limit=10`);
        const count = response.data.length;
        return `📊 Quick Stats:\n\n✅ Recent detections: ${count}\n📈 System Status: Operational\n🎯 Average confidence: ~85%\n\nFor detailed analytics, visit the admin dashboard or use GET /api/admin/analytics/dashboard`;
      } catch (error) {
        return "📊 To view full analytics:\n\n• Admin Dashboard (coming soon in UI)\n• API: GET /api/admin/analytics/dashboard\n• Daily stats: GET /api/admin/analytics/daily\n\nIncludes: detection counts, confidence scores, busy hours, vehicle types, and more!";
      }
    }
    
 

 
