import os
import sys
import json
import hashlib
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    required = ["README.md", "requirements.txt", "verify_automation.py"]
    missing = [f for f in required if not Path(f).exists()]
    if missing:
        print(f"Missing files: {missing}")
        sys.exit(1)

    evidence = {
        "files": {},
        "status": "ok"
    }
    for f in required:
        evidence["files"][f] = sha256_file(f)

    Path("evidence.json").write_text(json.dumps(evidence, indent=2))
    print("Verification passed - evidence.json created")

if __name__ == "__main__":
    main()
