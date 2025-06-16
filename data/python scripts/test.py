from pathlib import Path
import pandas as pd

# Update this path to match your actual file location
base_dir = Path("C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/TRADE AND TARIFF")
tariff_file = base_dir / "TARIFF.csv"

# Debug: Check if file exists
print(f"🔍 Looking for TARIFF.csv at: {tariff_file}")
if not tariff_file.exists():
    raise FileNotFoundError(f"❌ TARIFF.csv not found at {tariff_file}")

# Try reading the file
df_tariff_raw = pd.read_csv(tariff_file, header=None)
print(f"✅ Loaded TARIFF.csv, shape = {df_tariff_raw.shape}")

# Preview content to check formatting
print("\n🔎 First 10 rows:\n", df_tariff_raw.head(10))
