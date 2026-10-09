from ultralytics import YOLO
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_YAML = BASE_DIR / "dataset" / "final" / "data.yaml"

PROJECT_DIR = BASE_DIR / "runs"


# ==========================================
# LOAD YOLO MODEL
# ==========================================

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")


# ==========================================
# START TRAINING
# ==========================================

print("\nStarting training...")
print("Dataset:", DATA_YAML)

results = model.train(

    data=str(DATA_YAML),

    # Number of training rounds
    epochs=1,

    # Image size
    imgsz=640,

    # Batch size
    batch=8,

    # CPU training
    device="cpu",

    # Number of workers
    workers=2,

    # Save training results
    project=str(PROJECT_DIR),

    name="securevision_yolo",

    # Stop if validation doesn't improve
    patience=10,

    # Save best and last models
    save=True,

    # Show progress
    verbose=True
)


print("\n======================================")
print("TRAINING COMPLETED")
print("======================================")

print("\nResults saved in:")

print(
    PROJECT_DIR / "securevision_yolo"
)

print("\nBest model should be:")

print(
    PROJECT_DIR
    / "securevision_yolo"
    / "weights"
    / "best.pt"
)