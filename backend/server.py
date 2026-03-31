from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import cv2
import numpy as np
import shutil

from detector import PlateDetector
from ocr import PlateOCR
from utils import draw_detections, save_image, calculate_confidence_level
from ai_features import VehicleClassifier, PlateRegionDetector
from models import PlateDetection, DetectionResponse, BatchDetectionResponse, VehicleType


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create uploads and outputs directories
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize detector and OCR
plate_detector = PlateDetector()
plate_ocr = PlateOCR()

# Initialize AI features
vehicle_classifier = VehicleClassifier()
region_detector = PlateRegionDetector()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# ANPR Models
class PlateDetection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    plate_text: str
    confidence: float
    confidence_level: str
    detection_bbox: List[int]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    original_image_url: str
    annotated_image_url: str
    cropped_plate_url: str

class DetectionResponse(BaseModel):
    success: bool
    message: str
    detection: Optional[dict] = None
    
class BatchDetectionResponse(BaseModel):
    success: bool
    message: str
    detections: List[PlateDetection]
    total: int
    successful: int
    failed: int

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# ANPR Routes
@api_router.post("/detect/image", response_model=DetectionResponse)
async def detect_plate_image(file: UploadFile = File(...), fast_mode: bool = False):
    """
    Detect license plate in uploaded image
    
    Args:
        file: Image file
        fast_mode: Use fast preprocessing (faster but slightly less accurate)
    """
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        filename = f"{file_id}{file_ext}"
        upload_path = UPLOAD_DIR / filename
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read and enhance image
        image = cv2.imread(str(upload_path))
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Apply image enhancement for better detection
        from preprocessing import get_preprocessor
        preprocessor = get_preprocessor('fast' if fast_mode else 'advanced')
        enhanced_image = preprocessor.enhance_image(image)
        
        # Detect plates on enhanced image
        detections = plate_detector.detect(enhanced_image, conf_threshold=0.25)
        
        if not detections:
            # Fallback: try on original image
            detections = plate_detector.detect(image, conf_threshold=0.20)
            
            if not detections:
                return DetectionResponse(
                    success=False,
                    message="No license plate detected in the image. Try better lighting or front-facing view.",
                    detection=None
                )
        
        # Get the detection with highest confidence
        best_detection = max(detections, key=lambda x: x['confidence'])
        
        # Crop plate region from original image
        plate_crop = plate_detector.crop_plate(image, best_detection['bbox'])
        
        # Run advanced OCR with ensemble methods
        from ocr import PlateOCR
        advanced_ocr = PlateOCR(fast_mode=fast_mode)
        advanced_ocr.load_reader()
        plate_text, ocr_confidence = advanced_ocr.read_plate(plate_crop, use_ensemble=not fast_mode)
        
        if not plate_text:
            plate_text = "UNREADABLE"
            ocr_confidence = 0.0
        
        # Classify vehicle type
        vehicle_type = vehicle_classifier.classify(image, best_detection['bbox'])
        
        # Detect region
        plate_region = region_detector.detect_region(plate_text) if plate_text != "UNREADABLE" else None
        
        # Draw annotations
        annotated = draw_detections(image, [best_detection], [plate_text])
        
        # Save images
        annotated_filename = f"annotated_{filename}"
        cropped_filename = f"cropped_{file_id}.jpg"
        annotated_path = OUTPUT_DIR / annotated_filename
        cropped_path = OUTPUT_DIR / cropped_filename
        
        save_image(annotated, str(annotated_path))
        save_image(plate_crop, str(cropped_path))
        
        # Create enhanced detection record
        confidence_level = calculate_confidence_level(ocr_confidence)
        detection = PlateDetection(
            id=file_id,
            filename=file.filename,
            plate_text=plate_text,
            confidence=ocr_confidence,
            confidence_level=confidence_level,
            detection_bbox=best_detection['bbox'],
            vehicle_type=VehicleType(vehicle_type),
            plate_country=plate_region,
            original_image_url=f"/api/files/uploads/{filename}",
            annotated_image_url=f"/api/files/outputs/{annotated_filename}",
            cropped_plate_url=f"/api/files/outputs/{cropped_filename}"
        )
        
        # Save to MongoDB
        doc = detection.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.detections.insert_one(doc)
        
        return DetectionResponse(
            success=True,
            message=f"Successfully detected plate: {plate_text} (Vehicle: {vehicle_type}, Region: {plate_region or 'Unknown'})",
            detection=detection
        )
        
    except Exception as e:
        logger.error(f"Error in detect_plate_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/detect/batch", response_model=BatchDetectionResponse)
async def detect_plates_batch(files: List[UploadFile] = File(...)):
    """Detect license plates in multiple images"""
    detections = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Save uploaded file
            file_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix
            filename = f"{file_id}{file_ext}"
            upload_path = UPLOAD_DIR / filename
            
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Read image
            image = cv2.imread(str(upload_path))
            if image is None:
                failed += 1
                continue
            
            # Detect plates
            plate_detections = plate_detector.detect(image, conf_threshold=0.25)
            
            if not plate_detections:
                failed += 1
                continue
            
            # Process first detection
            best_detection = max(plate_detections, key=lambda x: x['confidence'])
            plate_crop = plate_detector.crop_plate(image, best_detection['bbox'])
            plate_text, ocr_confidence = plate_ocr.read_plate(plate_crop)
            
            if not plate_text:
                plate_text = "UNREADABLE"
                ocr_confidence = 0.0
            
            # Draw and save
            annotated = draw_detections(image, [best_detection], [plate_text])
            annotated_filename = f"annotated_{filename}"
            cropped_filename = f"cropped_{file_id}.jpg"
            
            save_image(annotated, str(OUTPUT_DIR / annotated_filename))
            save_image(plate_crop, str(OUTPUT_DIR / cropped_filename))
            
            # Create record
            confidence_level = calculate_confidence_level(ocr_confidence)
            detection = PlateDetection(
                id=file_id,
                filename=file.filename,
                plate_text=plate_text,
                confidence=ocr_confidence,
                confidence_level=confidence_level,
                detection_bbox=best_detection['bbox'],
                original_image_url=f"/api/files/uploads/{filename}",
                annotated_image_url=f"/api/files/outputs/{annotated_filename}",
                cropped_plate_url=f"/api/files/outputs/{cropped_filename}"
            )
            
            # Save to DB
            doc = detection.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.detections.insert_one(doc)
            
            detections.append(detection)
            successful += 1
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            failed += 1
    
    return BatchDetectionResponse(
        success=successful > 0,
        message=f"Processed {successful + failed} images: {successful} successful, {failed} failed",
        detections=detections,
        total=len(files),
        successful=successful,
        failed=failed
    )

@api_router.get("/detections", response_model=List[PlateDetection])
async def get_detections(limit: int = 50, skip: int = 0):
    """Get detection history"""
    try:
        detections = await db.detections.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
        
        # Convert timestamps
        for det in detections:
            if isinstance(det['timestamp'], str):
                det['timestamp'] = datetime.fromisoformat(det['timestamp'])
        
        return detections
    except Exception as e:
        logger.error(f"Error fetching detections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/detections/{detection_id}", response_model=PlateDetection)
async def get_detection(detection_id: str):
    """Get specific detection by ID"""
    try:
        detection = await db.detections.find_one({"id": detection_id}, {"_id": 0})
        if not detection:
            raise HTTPException(status_code=404, detail="Detection not found")
        
        if isinstance(detection['timestamp'], str):
            detection['timestamp'] = datetime.fromisoformat(detection['timestamp'])
        
        return detection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/detections/{detection_id}")
async def delete_detection(detection_id: str):
    """Delete a detection record"""
    try:
        result = await db.detections.delete_one({"id": detection_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Detection not found")
        return {"success": True, "message": "Detection deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/files/{folder}/{filename}")
async def get_file(folder: str, filename: str):
    """Serve uploaded or output files"""
    try:
        if folder == "uploads":
            file_path = UPLOAD_DIR / filename
        elif folder == "outputs":
            file_path = OUTPUT_DIR / filename
        else:
            raise HTTPException(status_code=400, detail="Invalid folder")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Import and include admin routes
try:
    from server_admin import admin_router
    # Create a wrapper to inject db dependency
    @admin_router.get("/test")
    async def test_admin():
        return {"message": "Admin routes loaded"}
    
    # Modify admin routes to accept db
    import inspect
    for route in admin_router.routes:
        if hasattr(route, 'endpoint'):
            sig = inspect.signature(route.endpoint)
            if 'db' in sig.parameters:
                # Wrap endpoint to inject db
                original_endpoint = route.endpoint
                async def wrapped_endpoint(*args, db_param=db, **kwargs):
                    return await original_endpoint(*args, db=db_param, **kwargs)
                route.endpoint = wrapped_endpoint
    
    api_router.include_router(admin_router)
    logger.info("Admin routes successfully loaded")
except Exception as e:
    logger.warning(f"Could not load admin routes: {e}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()