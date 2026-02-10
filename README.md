# JisCA_NOp - Advanced License Plate Recognition System

A production-ready, AI-powered ANPR (Automatic Number Plate Recognition) system with comprehensive admin panel, advanced AI features, and enterprise-grade deployment options.

## Features

### Core Detection
- **YOLOv8 Detection**: State-of-the-art license plate detection
- **EasyOCR Recognition**: Advanced OCR with intelligent preprocessing
- **Real-Time Processing**: Fast image and video processing
- **Batch Processing**: Upload and process multiple images simultaneously

### AI-Powered Features
- **Vehicle Classification**: Automatic vehicle type detection (car, truck, motorcycle, bus, van)
- **Region Detection**: Identify plate country/region from format patterns
- **Smart Fuzzy Search**: Find plates even with OCR errors using similarity matching
- **Duplicate Detection**: Identify repeated plate detections within time windows
- **Analytics Engine**: Comprehensive statistics and predictions
- **Busy Hours Prediction**: Identify peak detection times

### Admin Panel
- **Dashboard**: Real-time analytics with charts and statistics
- **User Management**: Complete CRUD operations for users with role-based access
- **Vehicle Database**: Maintain vehicle records with plate linking
- **Alert System**: Real-time alerts for stolen/wanted vehicles
- **API Key Management**: Generate and manage API keys with rate limiting
- **System Settings**: Configure detection thresholds and system parameters

### Enterprise Features
- **MongoDB Integration**: Persistent storage for all data
- **RESTful API**: Complete backend API for external integrations
- **Docker Support**: Containerized deployment with docker-compose
- **Kubernetes Ready**: Full K8s manifests with auto-scaling
- **Horizontal Scaling**: Built-in support for multiple replicas
- **Health Checks**: Liveness and readiness probes

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- YOLOv8 (Ultralytics)
- EasyOCR
- OpenCV
- MongoDB with Motor
- Pydantic for data validation

### Frontend
- React 19
- Tailwind CSS + Shadcn UI
- Framer Motion
- Axios
- React Router

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone <your-repo>
cd JisCA_NOp

# Start all services
docker-compose up -d

# Access application
# Frontend: http://localhost
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Local Development

#### Prerequisites
- Python 3.11+
- Node.js 18+ and Yarn
- MongoDB 6+

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Run server (port 8001)
uvicorn server:app --reload
```

#### Frontend Setup
```bash
cd frontend
yarn install
yarn start  # Port 3000
```

## YOLOv8 Model Setup

**Important**: For production accuracy, download a pre-trained license plate model:

1. Visit [Roboflow Universe](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e)
2. Export as YOLOv8 PyTorch format
3. Download `best.pt` file
4. Place in `/app/backend/models/best.pt`

Without a custom model, the system uses YOLOv8n (general object detection) which has limited plate detection accuracy.

## API Endpoints

### Detection
- `POST /api/detect/image` - Detect plate in single image
- `POST /api/detect/batch` - Batch process multiple images
- `GET /api/detections` - Get detection history
- `GET /api/detections/{id}` - Get specific detection
- `DELETE /api/detections/{id}` - Delete detection

### Admin Panel
- `GET /api/admin/users` - List users
- `POST /api/admin/users` - Create user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/vehicles` - List vehicles
- `POST /api/admin/vehicles` - Add vehicle
- `PUT /api/admin/vehicles/{id}` - Update vehicle
- `DELETE /api/admin/vehicles/{id}` - Delete vehicle
- `GET /api/admin/alerts` - Get alerts
- `PUT /api/admin/alerts/{id}/read` - Mark alert as read
- `GET /api/admin/analytics/dashboard` - Dashboard analytics
- `GET /api/admin/analytics/daily` - Daily analytics
- `GET /api/admin/api-keys` - List API keys
- `POST /api/admin/api-keys` - Create API key
- `DELETE /api/admin/api-keys/{id}` - Delete API key
- `GET /api/admin/settings` - Get system settings
- `PUT /api/admin/settings` - Update settings
- `GET /api/admin/search/fuzzy` - Fuzzy search plates
- `GET /api/admin/duplicates` - Find duplicate detections

## Database Collections

- **users**: User accounts with roles
- **detections**: License plate detection records
- **vehicles**: Vehicle database
- **alerts**: System alerts (stolen, wanted, suspicious)
- **api_keys**: API key management
- **daily_analytics**: Daily statistics
- **settings**: System configuration

## Kubernetes Deployment

### Quick Deploy
```bash
kubectl apply -f k8s/
```

### Step-by-Step
See [k8s/README.md](k8s/README.md) for detailed deployment guide including:
- Namespace creation
- Secret configuration
- MongoDB StatefulSet
- Backend/Frontend deployments
- Ingress setup
- Auto-scaling configuration
- Monitoring and troubleshooting

### Production Checklist
- [ ] Update secrets in `k8s/configmap.yaml`
- [ ] Configure domain in `k8s/ingress.yaml`
- [ ] Push Docker images to registry
- [ ] Set up MongoDB backups
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging (EFK stack)
- [ ] Implement RBAC policies
- [ ] Configure TLS with cert-manager

## Docker Deployment

### Build Images
```bash
# Backend
docker build -t jisca-nop-backend:latest ./backend

# Frontend
docker build -t jisca-nop-frontend:latest ./frontend
```

### Run with Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Configuration

### Environment Variables

#### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=jisca_nop
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### System Settings (via Admin Panel)
- Detection confidence threshold
- Alert enablement
- File size limits
- Data retention period
- SMTP configuration for email alerts

## AI Features Usage

### Vehicle Classification
```python
from ai_features import VehicleClassifier

classifier = VehicleClassifier()
vehicle_type = classifier.classify(image, bbox)
# Returns: car, truck, motorcycle, bus, van, unknown
```

### Smart Fuzzy Search
```python
from ai_features import SmartSearch

results = SmartSearch.fuzzy_match("ABC123", all_plates, threshold=0.8)
# Finds similar plates even with OCR errors
```

### Duplicate Detection
```python
from ai_features import DuplicateDetector

duplicates = DuplicateDetector.find_duplicates(detections, time_window_hours=24)
# Identifies repeated detections within time window
```

### Analytics
```python
from ai_features import AnalyticsEngine

stats = AnalyticsEngine.calculate_stats(detections)
busy_hours = AnalyticsEngine.predict_busy_hours(detections)
```

## Admin Panel Access

The admin panel provides a web interface for:
- Real-time dashboard with charts
- User and vehicle management
- Alert monitoring
- API key generation
- System configuration
- Analytics and reports

Access via: `http://localhost:3000/admin` (to be implemented in frontend)

## Performance Optimization

- **Model Selection**: Use YOLOv8n/s for speed, YOLOv8m for accuracy
- **Image Preprocessing**: Automatic optimization before OCR
- **Batch Processing**: Efficient multi-file handling
- **Async Operations**: Non-blocking database operations
- **Horizontal Scaling**: Multiple backend replicas in K8s
- **Auto-scaling**: HPA based on CPU/memory usage

## Security Best Practices

1. **API Keys**: Use API key authentication for external access
2. **Rate Limiting**: Configure rate limits per API key
3. **RBAC**: Implement role-based access control
4. **Secrets**: Use external secret managers in production
5. **TLS**: Enable HTTPS with Let's Encrypt
6. **Network Policies**: Restrict pod-to-pod communication

## Monitoring & Observability

### Health Checks
```bash
# Backend health
curl http://localhost:8001/api/

# Check services
kubectl get pods -n jisca-nop -w
```

### Metrics
- Detection count and success rate
- Average confidence scores
- Processing time per image
- API response times
- Resource usage (CPU/memory)

### Logging
- Application logs via supervisor
- Kubernetes logs via kubectl
- Centralized logging with EFK (recommended)

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log
# or in Docker
docker logs jisca_nop_backend
```

**Detection accuracy low:**
- Ensure custom YOLOv8 model is installed in `models/best.pt`
- Check image quality and lighting
- Adjust confidence threshold in settings

**MongoDB connection failed:**
- Verify MONGO_URL environment variable
- Check MongoDB service status
- Ensure proper network connectivity

**Frontend not loading:**
```bash
# Check frontend logs
docker logs jisca_nop_frontend
# Verify backend URL in .env
```

## Development

### Adding New Features
1. Backend: Add routes in `server.py` or `server_admin.py`
2. Database: Update models in `models.py`
3. AI: Extend features in `ai_features.py`
4. Frontend: Create React components/pages
5. Test: Run testing agent for validation

### Running Tests
```bash
# Backend
pytest backend/

# Frontend
cd frontend && yarn test
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support & Documentation

- **API Documentation**: Visit `/docs` endpoint (Swagger UI)
- **K8s Guide**: See `k8s/README.md`
- **Model Training**: See `backend/models/README.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Roadmap

- [ ] Real-time webcam stream processing
- [ ] Video file processing with frame extraction
- [ ] Multi-language OCR support (Arabic, Chinese, etc.)
- [ ] Mobile app (React Native)
- [ ] Webhook notifications
- [ ] CSV/Excel export
- [ ] Integration with vehicle databases
- [ ] Advanced analytics dashboard
- [ ] Machine learning model retraining pipeline

## Credits

- **YOLOv8**: Ultralytics
- **EasyOCR**: JaidedAI
- **UI Framework**: Shadcn UI
- **Icons**: Lucide React

---

**JisCA_NOp** - Advanced License Plate Recognition System
Built with cutting-edge AI technology for modern surveillance and security needs.
