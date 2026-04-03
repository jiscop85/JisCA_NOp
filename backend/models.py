"""Database models for JisCA_NOp ANPR system"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class VehicleType(str, Enum):
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    VAN = "van"
    UNKNOWN = "unknown"

class AlertType(str, Enum):
    STOLEN = "stolen"
    WANTED = "wanted"
    SUSPICIOUS = "suspicious"
    DUPLICATE = "duplicate"

# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER

# Detection Models (Enhanced)
class PlateDetection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    plate_text: str
    confidence: float
    confidence_level: str
    detection_bbox: List[int]
    vehicle_type: VehicleType = VehicleType.UNKNOWN
    plate_country: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    original_image_url: str
    annotated_image_url: str
    cropped_plate_url: str
    user_id: Optional[str] = None
    location: Optional[str] = None
    camera_id: Optional[str] = None
    is_flagged: bool = False
    notes: Optional[str] = None

# Vehicle Database
class Vehicle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plate_number: str
    vehicle_type: VehicleType
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    is_stolen: bool = False
    is_wanted: bool = False
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VehicleCreate(BaseModel):
    plate_number: str
    vehicle_type: VehicleType
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    is_stolen: bool = False
    is_wanted: bool = False
    notes: Optional[str] = None

# Alert System
class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detection_id: str
    plate_text: str
    alert_type: AlertType
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

# API Key Management
class APIKey(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    name: str
    user_id: str
    is_active: bool = True
    usage_count: int = 0
    rate_limit: int = 1000  # requests per day
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class APIKeyCreate(BaseModel):
    name: str
    rate_limit: int = 1000

# Analytics
class DailyAnalytics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime
    total_detections: int = 0
    successful_detections: int = 0
    failed_detections: int = 0
    unique_plates: int = 0
    alerts_generated: int = 0
    avg_confidence: float = 0.0
    vehicle_types: Dict[str, int] = {}

# System Settings
class SystemSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = "system_settings"
    confidence_threshold: float = 0.25
    enable_alerts: bool = True
    enable_analytics: bool = True
    max_file_size_mb: int = 10
    retention_days: int = 30
    smtp_enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
