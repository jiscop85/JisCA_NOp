"""Admin panel and AI features endpoints for JisCA_NOp"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging

from models import (
    User, UserCreate, Vehicle, VehicleCreate, Alert, APIKey, APIKeyCreate,
    DailyAnalytics, SystemSettings, VehicleType, AlertType
)
from ai_features import (
    VehicleClassifier, PlateRegionDetector, SmartSearch,
    DuplicateDetector, AnalyticsEngine
)

logger = logging.getLogger(__name__)

# Initialize AI features
vehicle_classifier = VehicleClassifier()
region_detector = PlateRegionDetector()
analytics_engine = AnalyticsEngine()

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# User Management
@admin_router.get("/users", response_model=List[User])
async def get_users(db, skip: int = 0, limit: int = 50):
    """Get all users"""
    try:
        users = await db.users.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        for user in users:
            if isinstance(user.get('created_at'), str):
                user['created_at'] = datetime.fromisoformat(user['created_at'])
            if isinstance(user.get('last_login'), str):
                user['last_login'] = datetime.fromisoformat(user['last_login'])
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/users", response_model=User)
async def create_user(db, user_data: UserCreate):
    """Create new user"""
    try:
        # In production, hash the password properly
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        doc = user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc.get('last_login'):
            doc['last_login'] = doc['last_login'].isoformat()
        
        await db.users.insert_one(doc)
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/users/{user_id}")
async def delete_user(db, user_id: str):
    """Delete user"""
    try:
        result = await db.users.delete_one({"id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vehicle Database
@admin_router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles(db, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    """Get vehicles from database"""
    try:
        query = {}
        if search:
            query = {"plate_number": {"$regex": search, "$options": "i"}}
        
        vehicles = await db.vehicles.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        for vehicle in vehicles:
            if isinstance(vehicle.get('created_at'), str):
                vehicle['created_at'] = datetime.fromisoformat(vehicle['created_at'])
            if isinstance(vehicle.get('updated_at'), str):
                vehicle['updated_at'] = datetime.fromisoformat(vehicle['updated_at'])
        return vehicles
    except Exception as e:
        logger.error(f"Error fetching vehicles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(db, vehicle_data: VehicleCreate):
    """Add vehicle to database"""
    try:
        vehicle = Vehicle(**vehicle_data.model_dump())
        
        doc = vehicle.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        
        await db.vehicles.insert_one(doc)
        return vehicle
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(db, vehicle_id: str, vehicle_data: VehicleCreate):
    """Update vehicle information"""
    try:
        update_data = vehicle_data.model_dump()
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = await db.vehicles.update_one(
            {"id": vehicle_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle = await db.vehicles.find_one({"id": vehicle_id}, {"_id": 0})
        if isinstance(vehicle['created_at'], str):
            vehicle['created_at'] = datetime.fromisoformat(vehicle['created_at'])
        if isinstance(vehicle['updated_at'], str):
            vehicle['updated_at'] = datetime.fromisoformat(vehicle['updated_at'])
        
        return vehicle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(db, vehicle_id: str):
    """Delete vehicle"""
    try:
        result = await db.vehicles.delete_one({"id": vehicle_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return {"success": True, "message": "Vehicle deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Alerts
@admin_router.get("/alerts", response_model=List[Alert])
async def get_alerts(db, unread_only: bool = False, limit: int = 50):
    """Get system alerts"""
    try:
        query = {"is_read": False} if unread_only else {}
        alerts = await db.alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        for alert in alerts:
            if isinstance(alert.get('created_at'), str):
                alert['created_at'] = datetime.fromisoformat(alert['created_at'])
            if isinstance(alert.get('resolved_at'), str):
                alert['resolved_at'] = datetime.fromisoformat(alert['resolved_at'])
        
        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/alerts/{alert_id}/read")
async def mark_alert_read(db, alert_id: str):
    """Mark alert as read"""
    try:
        result = await db.alerts.update_one(
            {"id": alert_id},
            {"$set": {"is_read": True}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"success": True, "message": "Alert marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics
@admin_router.get("/analytics/dashboard")
async def get_dashboard_analytics(db):
    """Get dashboard analytics"""
    try:
        # Get recent detections
        detections = await db.detections.find({}, {"_id": 0}).sort("timestamp", -1).limit(1000).to_list(1000)
        
        # Parse timestamps
        for det in detections:
            if isinstance(det.get('timestamp'), str):
                det['timestamp'] = datetime.fromisoformat(det['timestamp'])
        
        # Calculate statistics
        stats = analytics_engine.calculate_stats(detections)
        
        # Get time-based stats
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        today_detections = [d for d in detections if d['timestamp'] >= today_start]
        week_detections = [d for d in detections if d['timestamp'] >= week_start]
        
        # Busy hours prediction
        busy_hours = analytics_engine.predict_busy_hours(week_detections) if week_detections else []
        
        # Find duplicates
        duplicates = DuplicateDetector.find_duplicates(week_detections, time_window_hours=24)
        
        return {
            "overall": stats,
            "today": {
                "total": len(today_detections),
                "unique_plates": len(set(d['plate_text'] for d in today_detections))
            },
            "week": {
                "total": len(week_detections),
                "unique_plates": len(set(d['plate_text'] for d in week_detections)),
                "avg_per_day": len(week_detections) / 7
            },
            "busy_hours": busy_hours,
            "duplicates_count": len(duplicates),
            "alerts_count": await db.alerts.count_documents({"is_read": False})
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/analytics/daily", response_model=List[DailyAnalytics])
async def get_daily_analytics(db, days: int = 30):
    """Get daily analytics for chart"""
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        analytics = await db.daily_analytics.find(
            {"date": {"$gte": start_date.isoformat()}},
            {"_id": 0}
        ).sort("date", -1).to_list(days)
        
        for item in analytics:
            if isinstance(item.get('date'), str):
                item['date'] = datetime.fromisoformat(item['date'])
        
        return analytics
    except Exception as e:
        logger.error(f"Error fetching daily analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API Key Management
@admin_router.get("/api-keys", response_model=List[APIKey])
async def get_api_keys(db):
    """Get all API keys"""
    try:
        keys = await db.api_keys.find({}, {"_id": 0}).to_list(100)
        for key in keys:
            if isinstance(key.get('created_at'), str):
                key['created_at'] = datetime.fromisoformat(key['created_at'])
            if isinstance(key.get('expires_at'), str):
                key['expires_at'] = datetime.fromisoformat(key['expires_at'])
        return keys
    except Exception as e:
        logger.error(f"Error fetching API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/api-keys", response_model=APIKey)
async def create_api_key(db, key_data: APIKeyCreate, user_id: str):
    """Create new API key"""
    try:
        import secrets
        api_key = APIKey(
            key=secrets.token_urlsafe(32),
            name=key_data.name,
            user_id=user_id,
            rate_limit=key_data.rate_limit
        )
        
        doc = api_key.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc.get('expires_at'):
            doc['expires_at'] = doc['expires_at'].isoformat()
        
        await db.api_keys.insert_one(doc)
        return api_key
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/api-keys/{key_id}")
async def delete_api_key(db, key_id: str):
    """Delete API key"""
    try:
        result = await db.api_keys.delete_one({"id": key_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")
        return {"success": True, "message": "API key deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Settings
@admin_router.get("/settings", response_model=SystemSettings)
async def get_settings(db):
    """Get system settings"""
    try:
        settings = await db.settings.find_one({"id": "system_settings"}, {"_id": 0})
        if not settings:
            # Create default settings
            settings = SystemSettings().model_dump()
            settings['updated_at'] = settings['updated_at'].isoformat()
            await db.settings.insert_one(settings)
            settings['updated_at'] = datetime.fromisoformat(settings['updated_at'])
        else:
            if isinstance(settings.get('updated_at'), str):
                settings['updated_at'] = datetime.fromisoformat(settings['updated_at'])
        return settings
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/settings", response_model=SystemSettings)
async def update_settings(db, settings: SystemSettings):
    """Update system settings"""
    try:
        settings.updated_at = datetime.now(timezone.utc)
        doc = settings.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        
        await db.settings.update_one(
            {"id": "system_settings"},
            {"$set": doc},
            upsert=True
        )
        
        return settings
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart Search
@admin_router.get("/search/fuzzy")
async def fuzzy_search_plates(db, query: str, threshold: float = 0.8):
    """Fuzzy search for plates"""
    try:
        # Get all plates
        detections = await db.detections.find({}, {"plate_text": 1, "_id": 0}).to_list(1000)
        plates = [d['plate_text'] for d in detections]
        
        # Perform fuzzy search
        results = SmartSearch.fuzzy_match(query, plates, threshold)
        
        return {
            "query": query,
            "results": [{"plate": plate, "score": score} for plate, score in results[:20]]
        }
    except Exception as e:
        logger.error(f"Error in fuzzy search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Duplicate Detection
@admin_router.get("/duplicates")
async def find_duplicate_detections(db, hours: int = 24):
    """Find duplicate detections"""
    try:
        # Get recent detections
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        detections = await db.detections.find(
            {"timestamp": {"$gte": cutoff.isoformat()}},
            {"_id": 0}
        ).to_list(1000)
        
        # Parse timestamps
        for det in detections:
            if isinstance(det['timestamp'], str):
                det['timestamp'] = datetime.fromisoformat(det['timestamp'])
        
        # Find duplicates
        duplicates = DuplicateDetector.find_duplicates(detections, time_window_hours=hours)
        
        return {
            "time_window_hours": hours,
            "duplicate_groups": len(duplicates),
            "duplicates": duplicates
        }
    except Exception as e:
        logger.error(f"Error finding duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
