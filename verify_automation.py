import sys
import json
import hashlib
from pathlib import Path

REQUIRED_FILES = ["README.md", "requirements.txt", "verify_automation.py"]
EVIDENCE_FILE = Path("evidence.json")

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    missing = [f for f in REQUIRED_FILES if not Path(f).exists()]
    if missing:
        print(f"Missing files: {missing}")
        sys.exit(1)

    evidence = {
        "status": "ok",
        "files": {f: sha256_file(Path(f)) for f in REQUIRED_FILES},
    }

    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2))
    print("Verification passed - evidence.json created")

if __name__ == "__main__":
    main()