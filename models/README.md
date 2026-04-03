# Models Directory

This directory contains pre-trained YOLOv8 models for license plate detection.

## Model Files

### Recommended: Custom License Plate Model

For production use, download a pre-trained license plate detection model:

1. Visit [Roboflow Universe](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e)
2. Export as YOLOv8 PyTorch format
3. Download `best.pt` file
4. Place in this directory as `best.pt`

### Default Model

If no custom model is found, the system will use YOLOv8n (nano) from Ultralytics, which is a general object detection model. This model has limited accuracy for license plate detection and should only be used for testing.

## Model Requirements

- **Format**: PyTorch (.pt) file
- **Architecture**: YOLOv8 (any variant: n, s, m, l, x)
- **Input Size**: 640x640 (standard YOLOv8 input)
- **Classes**: Should include license plate class

## Model Performance

### Custom License Plate Model
- **Accuracy**: 85-95% (depending on training data)
- **Speed**: 20-50ms per image (GPU), 100-300ms (CPU)
- **Recommended for**: Production use

### YOLOv8n (Default)
- **Accuracy**: 30-50% (not optimized for plates)
- **Speed**: 10-30ms per image (GPU), 50-150ms (CPU)
- **Recommended for**: Testing only

## Model Training

To train your own model:

1. Collect license plate images
2. Annotate with bounding boxes
3. Use YOLOv8 training script:
   ```bash
   yolo train data=your_dataset.yaml model=yolov8n.pt epochs=100
   ```
4. Export best model to `best.pt`

## Model Configuration

Model path can be configured in:
- Environment variable: `MODEL_PATH`
- Default location: `backend/models/best.pt`
- Fallback: `yolov8n.pt` (root directory)

## Notes

- Models are loaded once at startup
- GPU acceleration is automatically used if available
- Model size affects inference speed vs accuracy trade-off

