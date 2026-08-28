
import sys
import subprocess

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Path: {sys.path}")

try:
    import pandas
    print(f"Pandas found at: {pandas.__file__}")
except ImportError:
    print("Pandas NOT found in current path.")

# Try to find other pythons
try:
    res = subprocess.run(["where", "python"], capture_output=True, text=True)
    print(f"Where python: {res.stdout}")
except: pass
