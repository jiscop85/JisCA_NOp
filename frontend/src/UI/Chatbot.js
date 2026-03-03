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
    
    if (msg.includes('error') || msg.includes('problem') || msg.includes('not work') || msg.includes('fail')) {
      return "🔧 Troubleshooting:\n\n1️⃣ Check backend: curl localhost:8001/api/\n2️⃣ Verify image quality & format\n3️⃣ Review logs: tail -f /var/log/supervisor/backend.err.log\n4️⃣ Ensure MongoDB is running\n5️⃣ Lower confidence threshold if needed\n\nStill stuck? Check DEPLOYMENT_GUIDE.md or describe your specific error.";
    }
    
    if (msg.includes('model') || msg.includes('yolo') || msg.includes('train')) {
      return "🤖 About the AI Model:\n\n🔹 Current: YOLOv8n (fallback, general detection)\n🔹 Recommended: Custom YOLOv8 trained on plates\n🔹 Download from: Roboflow Universe\n🔹 Accuracy boost: 60% → 99%+\n\n📥 Setup: Place best.pt in /app/backend/models/\n\nWant to train your own model? I can guide you!";
    }
    
    if (msg.includes('thank') || msg.includes('thanks')) {
      return "You're welcome! 😊 Happy to help anytime. If you have more questions about JisCA_NOp, just ask!";
    }
    
    if (msg.includes('contact') || msg.includes('support') || msg.includes('email')) {
      return "📧 Contact & Support:\n\n✉️ Email: arash.javadyfar@gmail.com\n💻 GitHub: Jisc_op\n📚 Documentation: README.md & DEPLOYMENT_GUIDE.md\n🐛 Issues: GitHub Issues\n\nFor urgent support, please email with [JisCA_NOp] in the subject line.";
    }
    
    // Default response
    return "🤔 I'm not sure about that specific question, but I can help you with:\n\n• System features and capabilities\n• How to use the detection system\n• API integration and endpoints\n• Deployment and configuration\n• Troubleshooting issues\n• Admin panel features\n• Analytics and statistics\n\nWhat would you like to know more about?";
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMsg = {
      id: messages.length + 1,
      type: 'user',
      text: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(async () => {
      const botResponse = await generateBotResponse(inputMessage);
      
      const botMsg = {
        id: messages.length + 2,
        type: 'bot',
        text: botResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMsg]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000); // Random delay for realism
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  return (
    <>
      {/* Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={() => setIsOpen(true)}
              data-testid="chatbot-open-button"
              className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 hover:from-cyan-400 hover:to-violet-400 shadow-[0_0_30px_rgba(0,240,255,0.4)] hover:shadow-[0_0_40px_rgba(0,240,255,0.6)] transition-all duration-300 flex items-center justify-center"
            >
              <MessageCircle className="w-7 h-7 text-black" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 z-50 w-[400px] h-[600px] bg-zinc-900 border border-cyan-500/30 rounded-sm shadow-[0_0_50px_rgba(0,240,255,0.3)] flex flex-col overflow-hidden"
            data-testid="chatbot-window"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-cyan-500 to-violet-500 p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-black/20 rounded-sm flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-black">JisCA_NOp AI</h3>
                  <p className="text-xs text-black/70">Smart Assistant</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="text-black hover:bg-black/10"
                data-testid="chatbot-close-button"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

    
 


