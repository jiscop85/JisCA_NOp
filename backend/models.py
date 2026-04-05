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

