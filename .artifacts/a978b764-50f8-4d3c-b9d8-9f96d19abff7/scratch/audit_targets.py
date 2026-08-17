import pandas as pd
import os
import glob

def audit():
    feature_dir = "backend/data/features"
    files = glob.glob(os.path.join(feature_dir, "*.parquet"))

    all_targets = []

    print(f"[*] Auditing {len(files)} feature files...")
    for f in files:
        df = pd.read_parquet(f)
        if 'target' in df.columns:
            all_targets.append(df['target'].dropna())

    if not all_targets:
        print("[!] No targets found.")
        return

    targets = pd.concat(all_targets)
    print("\n--- Target Distribution ---")
    print(targets.value_counts(normalize=True))
    print(f"Total labeled samples: {len(targets)}")

if __name__ == "__main__":
    audit()
