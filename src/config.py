from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "Data" / "Raw"
PROCESSED_DATA = BASE_DIR / "Data" / "Processed"
MODELS = BASE_DIR / "Models"
ASSETS = BASE_DIR / "Assets"