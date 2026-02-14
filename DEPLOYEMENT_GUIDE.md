# JisCA_NOp - Complete Deployment & Usage Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Database Schema](#database-schema)
4. [AI Features](#ai-features)
5. [Admin Panel](#admin-panel)
6. [Deployment Options](#deployment-options)
7. [API Reference](#api-reference)

## System Overview

JisCA_NOp is an enterprise-grade ANPR system with:
- **Core Detection**: YOLOv8 + EasyOCR
- **AI Features**: Vehicle classification, region detection, smart search
- **Admin Panel**: Complete management interface
- **Scalable**: Docker + Kubernetes ready
- **Database**: 7 MongoDB collections for comprehensive data management

## Quick Start

### Option 1: Docker Compose (Easiest)
```bash
docker-compose up -d
# Frontend: http://localhost
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Option 2: Local Development
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload

# Terminal 2 - Frontend
cd frontend
yarn install
yarn start
```

## Database Schema

### 1. users
User authentication and management
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "admin|user|viewer",
  "is_active": true,
  "created_at": "2025-01-24T...",
  "last_login": "2025-01-24T..."
}
```

**Roles:**
- `admin`: Full system access
- `user`: Detection and viewing
- `viewer`: Read-only access

### 2. detections
License plate detection records (enhanced)
```json
{
  "id": "uuid",
  "filename": "car.jpg",
  "plate_text": "ABC1234",
  "confidence": 0.92,
  "confidence_level": "high",
  "detection_bbox": [100, 150, 300, 250],
  "vehicle_type": "car",
  "plate_country": "USA",
  "timestamp": "2025-01-24T...",
  "original_image_url": "/api/files/uploads/...",
  "annotated_image_url": "/api/files/outputs/...",
  "cropped_plate_url": "/api/files/outputs/...",
  "user_id": "uuid",
  "location": "Camera-1",
  "camera_id": "cam_001",
  "is_flagged": false,
  "notes": "Optional notes"
}
```

### 3. vehicles
Vehicle database for plate tracking
```json
{
  "id": "uuid",
  "plate_number": "ABC1234",
  "vehicle_type": "car",
  "make": "Toyota",
  "model": "Camry",
  "color": "Silver",
  "year": 2020,
  "owner_name": "John Doe",
  "owner_phone": "+1234567890",
  "is_stolen": false,
  "is_wanted": false,
  "notes": "Regular visitor",
  "created_at": "2025-01-24T...",
  "updated_at": "2025-01-24T..."
}
```

### 4. alerts
Real-time alert system
```json
{
  "id": "uuid",
  "detection_id": "uuid",
  "plate_text": "XYZ789",
  "alert_type": "stolen|wanted|suspicious|duplicate",
  "message": "Vehicle reported stolen",
  "is_read": false,
  "created_at": "2025-01-24T...",
  "resolved_at": null
}
```

**Alert Types:**
- `stolen`: Plate matches stolen vehicle database
- `wanted`: Plate on wanted list
- `suspicious`: Multiple detections in short time
- `duplicate`: Same plate detected repeatedly

### 5. api_keys
API key management for external integrations
```json
{
  "id": "uuid",
  "key": "generated_key_32_chars",
  "name": "Mobile App",
  "user_id": "uuid",
  "is_active": true,
  "usage_count": 1250,
  "rate_limit": 10000,
  "created_at": "2025-01-24T...",
  "expires_at": "2026-01-24T..."
}
```

### 6. daily_analytics
Daily statistics for dashboard
```json
{
  "id": "uuid",
  "date": "2025-01-24",
  "total_detections": 1523,
  "successful_detections": 1489,
  "failed_detections": 34,
  "unique_plates": 876,
  "alerts_generated": 12,
  "avg_confidence": 0.87,
  "vehicle_types": {
    "car": 1200,
    "truck": 200,
    "motorcycle": 100,
    "bus": 20,
    "van": 3
  }
}
```

### 7. settings
System configuration
```json
{
  "id": "system_settings",
  "confidence_threshold": 0.25,
  "enable_alerts": true,
  "enable_analytics": true,
  "max_file_size_mb": 10,
  "retention_days": 30,
  "smtp_enabled": false,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "alerts@example.com",
  "updated_at": "2025-01-24T..."
}
```

## AI Features

### 1. Vehicle Classification
Automatically detects vehicle type from image
```python
# Backend usage
vehicle_type = vehicle_classifier.classify(image, bbox)
# Returns: car, truck, motorcycle, bus, van, unknown
```

**API**: Automatically included in detection response

### 2. Plate Region Detection
Identifies country/region from plate format
```python
# Backend usage
region = region_detector.detect_region("ABC1234")
# Returns: USA, UK, EU, or None
```

**Patterns:**
- USA: `ABC123`, `123ABC`
- UK: `AB12CDE`
- EU: `A123BC`, `AB1234`

### 3. Smart Fuzzy Search
Find plates even with OCR errors
```bash
GET /api/admin/search/fuzzy?query=ABC123&threshold=0.8
```

**Response:**
```json
{
  "query": "ABC123",
  "results": [
    {"plate": "ABC123", "score": 1.0},
    {"plate": "ABC1Z3", "score": 0.83},
    {"plate": "ABD123", "score": 0.83}
  ]
}
```

### 4. Duplicate Detection
Find repeated detections within time window
```bash
GET /api/admin/duplicates?hours=24
```

**Use Cases:**
- Identify suspicious repeated entries
- Track vehicle movements
- Detect potential fraud

### 5. Analytics Engine
Comprehensive statistics and predictions
```bash
GET /api/admin/analytics/dashboard
```

**Returns:**
- Overall statistics
- Today's detections
- Weekly trends
- Busy hours prediction
- Duplicate counts
- Unread alerts

## Admin Panel API

### User Management
```bash
# List users
GET /api/admin/users?skip=0&limit=50

# Create user
POST /api/admin/users
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "role": "user"
}

# Delete user
DELETE /api/admin/users/{user_id}
```

### Vehicle Database
```bash
# List vehicles
GET /api/admin/vehicles?search=ABC

# Add vehicle
POST /api/admin/vehicles
{
  "plate_number": "ABC1234",
  "vehicle_type": "car",
  "make": "Toyota",
  "model": "Camry",
  "owner_name": "John Doe",
  "is_stolen": false
}

# Update vehicle
PUT /api/admin/vehicles/{vehicle_id}
{...}

# Delete vehicle
DELETE /api/admin/vehicles/{vehicle_id}
```

### Alert Management
```bash
# Get alerts (unread only)
GET /api/admin/alerts?unread_only=true&limit=50

# Mark alert as read
PUT /api/admin/alerts/{alert_id}/read
```

### API Key Management
```bash
# List keys
GET /api/admin/api-keys

# Create key
POST /api/admin/api-keys?user_id={user_id}
{
  "name": "Mobile App",
  "rate_limit": 10000
}

# Delete key
DELETE /api/admin/api-keys/{key_id}
```

### System Settings
```bash
# Get settings
GET /api/admin/settings

# Update settings
PUT /api/admin/settings
{
  "confidence_threshold": 0.3,
  "enable_alerts": true,
  "max_file_size_mb": 15,
  "retention_days": 60
}
```

## Deployment Options

### 1. Development (Local)
```bash
# See Quick Start above
```

### 2. Production (Docker Compose)
```bash
# Update environment variables
vim docker-compose.yml

# Update MongoDB password
export MONGO_PASSWORD=your_secure_password

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 3. Enterprise (Kubernetes)
```bash
# Update secrets
vim k8s/configmap.yaml

# Deploy
kubectl apply -f k8s/

# Monitor
kubectl get pods -n jisca-nop -w
kubectl logs -f deployment/backend -n jisca-nop

# Scale
kubectl scale deployment backend --replicas=5 -n jisca-nop
```

**See k8s/README.md for detailed Kubernetes guide**

## API Reference

### Core Detection Endpoints

#### Single Image Detection
```bash
POST /api/detect/image
Content-Type: multipart/form-data

file: <image_file>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully detected plate: ABC1234",
  "detection": {
    "id": "uuid",
    "plate_text": "ABC1234",
    "confidence": 0.92,
    "vehicle_type": "car",
    "annotated_image_url": "/api/files/outputs/...",
    ...
  }
}
```

#### Batch Processing
```bash
POST /api/detect/batch
Content-Type: multipart/form-data

files: <image_file_1>
files: <image_file_2>
...
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 10 images: 9 successful, 1 failed",
  "detections": [...],
  "total": 10,
  "successful": 9,
  "failed": 1
}
```

#### Get Detection History
```bash
GET /api/detections?limit=50&skip=0
```

#### Get Specific Detection
```bash
GET /api/detections/{detection_id}
```

#### Delete Detection
```bash
DELETE /api/detections/{detection_id}
```

### File Serving
```bash
GET /api/files/uploads/{filename}
GET /api/files/outputs/{filename}
```

## Model Setup

**Critical for Production Accuracy:**

1. Download YOLOv8 license plate model from [Roboflow Universe](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e)
2. Export as YOLOv8 PyTorch format
3. Place `best.pt` in `/app/backend/models/`
4. Restart backend

**Without custom model**: System uses YOLOv8n with limited accuracy

## Performance Tuning

### Backend Optimization
```python
# In server.py, adjust:
conf_threshold=0.25  # Lower = more detections, higher = more accuracy
```

### Resource Limits (Kubernetes)
```yaml
# In k8s/backend.yaml
resources:
  requests:
    memory: "2Gi"  # Adjust based on load
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Auto-scaling
```yaml
# In k8s/hpa.yaml
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 70
```

## Monitoring

### Health Checks
```bash
# Backend
curl http://localhost:8001/api/

# Kubernetes
kubectl get pods -n jisca-nop
kubectl describe pod <pod-name> -n jisca-nop
```

### Logs
```bash
# Docker
docker logs -f jisca_nop_backend
docker logs -f jisca_nop_frontend

# Kubernetes
kubectl logs -f deployment/backend -n jisca-nop
kubectl logs -f deployment/frontend -n jisca-nop

# Local
tail -f /var/log/supervisor/backend.err.log
```

### Metrics to Monitor
- Detection success rate
- Average confidence scores
- Processing time per image
- API response times
- Memory/CPU usage
- Database size
- Alert frequency

## Security Checklist

- [ ] Change default MongoDB password
- [ ] Configure API key authentication
- [ ] Set up rate limiting
- [ ] Enable HTTPS with TLS certificates
- [ ] Implement RBAC for admin access
- [ ] Use external secret manager (Vault, AWS Secrets)
- [ ] Configure network policies in K8s
- [ ] Regular security audits
- [ ] Database backups
- [ ] Log monitoring and alerting

## Troubleshooting

### Backend Issues
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Restart service
sudo supervisorctl restart backend

# Test API
curl http://localhost:8001/api/
```

### Detection Not Working
1. Check if model file exists: `ls -la /app/backend/models/`
2. Verify image quality and lighting
3. Lower confidence threshold in settings
4. Check backend logs for errors

### MongoDB Connection Failed
```bash
# Check MongoDB service
docker ps | grep mongo
kubectl get pods -n jisca-nop | grep mongodb

# Verify connection string
echo $MONGO_URL
```

### High Memory Usage
- Reduce batch size
- Adjust model (use YOLOv8n instead of YOLOv8m)
- Increase memory limits in K8s
- Implement request queuing

## Advanced Configuration

### Custom Preprocessing
Edit `backend/ocr.py`:
```python
def preprocess_plate(self, plate_img):
    # Customize preprocessing steps
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    # Add your custom preprocessing
    return processed_image
```

### Custom Vehicle Classification
Edit `backend/ai_features.py`:
```python
def classify(self, image, bbox):
    # Implement custom classification logic
    # Can integrate with separate ML model
    return vehicle_type
```

### Email Alerts
Configure in Admin Panel settings:
```json
{
  "smtp_enabled": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "alerts@yourdomain.com"
}
```

## Support

- **Documentation**: See README.md and k8s/README.md
- **API Docs**: http://localhost:8001/docs (Swagger UI)
- **Issues**: Report via GitHub Issues
- **Questions**: GitHub Discussions

---

**JisCA_NOp** - Enterprise-grade License Plate Recognition
Built for security, surveillance, and smart city applications.
