import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\TRIDELL\Desktop\vinuni\part2")
scripts = [
    BASE / "src" / "charts_batch1.py",
    BASE / "src" / "charts_batch2.py",
    BASE / "src" / "charts_batch3.py",
    BASE / "direction1_loss_leaders" / "loss_leader_analysis.py",
    BASE / "direction2_logistics_churn" / "logistics_analysis.py",
    BASE / "direction3_product_lifecycle" / "product_lifecycle_analysis.py",
    BASE / "direction4_returns_sizing" / "returns_analysis.py"
]

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

for s in scripts:
    print(f"\n--- Running {s.name} ---")
    res = subprocess.run([sys.executable, str(s)])
    if res.returncode != 0:
        print(f"Failed {s.name}")
print("ALL DONE")
