# verify_aep.py v0.1.1 - XA-TRUST AEP Logical Envelope - FINAL
# Marco: STRUCTURAL AND VERIFIER IDENTITY VALIDATION + FROZEN BASELINE
# python verify_aep.py generate | python verify_aep.py verify
import json, hashlib, os, sys, re
from pathlib import Path
import rfc8785

EXPECTED_FILES = {"README.md", "requirements.txt", "verify_automation.py"}
EXPECTED_VERSION = "0.1.1-logical"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# FROZEN BASELINE - valores históricos da run 43709177738
# Recuperados do evidence.json original. NÃO calcular dos arquivos atuais.
FROZEN_BASELINE = {
    "README.md": "fd3dee8bf0a8a3810cce214c37766a5317cffd1ad7f06ae30cc22e854af12f81",
    "requirements.txt": "3c107420df879ffd72e3f705859e26f2073c19884c6fff37c342a3be4f600b9e",
    "verify_automation.py": "80e96c38c5ac0fb66abe7476b8caa5c08b940d14d0e5e27fd8604940005d269d"
}

POLICY_DOC = {"id": "verify-global", "version": "1.0", "rules": ["hash-must-match", "files-exact-set", "jcs-rfc8785"]}

def canonical(obj):
    try:
        return rfc8785.dumps(obj)
    except Exception as e:
        fail(f"JCS falhou: {e}")

def sha256(b: bytes): return hashlib.sha256(b).hexdigest()
def fail(msg): raise ValueError(msg)

def require_hash(value, field):
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        fail(f"{field}: SHA256 inválido")
    return value

def safe_path(filename):
    if filename not in EXPECTED_FILES:
        fail(f"Fora do contrato: {filename}")
    if "/" in filename or "\\" in filename or ".." in filename:
        fail(f"Caminho inválido: {filename}")
    p = Path(filename)
    if p.is_symlink():
        fail(f"Symlink não permitido: {filename}")
    try:
        p.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        fail(f"Fora da raiz: {filename}")
    return p

def load_json_utf8(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"JSON inválido em {path}: {e}")
    except OSError as e:
        fail(f"Erro de leitura em {path}: {e}")

def validate_frozen_baseline(files_dict):
    if not isinstance(files_dict, dict):
        fail("LEGACY_FILES_SCHEMA_INVALID")
    if set(files_dict) != EXPECTED_FILES:
        fail("LEGACY_FILES_SET_MISMATCH")
    if not isinstance(FROZEN_BASELINE, dict):
        fail("FROZEN_BASELINE_SCHEMA_INVALID")
    if set(FROZEN_BASELINE) != EXPECTED_FILES:
        fail("FROZEN_BASELINE_SCHEMA_INVALID")
    for filename, frozen_hash in FROZEN_BASELINE.items():
        require_hash(frozen_hash, f"FROZEN_BASELINE.{filename}")
        actual = sha256(safe_path(filename).read_bytes())
        if actual != frozen_hash:
            fail(f"FROZEN_BASELINE_IDENTITY_MISMATCH: {filename}")
        if files_dict.get(filename) != frozen_hash:
            fail(f"LEGACY_MANIFEST_BASELINE_MISMATCH: {filename}")
    return True

def load_legacy():
    p = Path("evidence.json")
    if not p.is_file(): fail("evidence.json não encontrado")
    legacy = load_json_utf8(p)
    if legacy.get("status") != "ok": fail("legado status != ok")
    if set(legacy.get("files", {})) != EXPECTED_FILES:
        fail("Conjunto diferente do contrato")
    for k, v in legacy["files"].items():
        require_hash(v, f"legacy.files.{k}")
    return legacy, p

def validate_files(files_dict, context=""):
    for filename, expected in files_dict.items():
        p = safe_path(filename)
        if not p.is_file(): fail(f"Ausente {context}: {filename}")
        if sha256(p.read_bytes()) != expected:
            fail(f"Hash divergente {context}: {filename}")

def validate_structure(aep):
    for k in ["proof_type", "version", "intent", "authority", "policy", "execution", "evidence_ref", "verifier", "proof_hash"]:
        if k not in aep: fail(f"Sem campo: {k}")
    if aep["proof_type"] != "AEP": fail("proof_type inválido")
    if aep["version"] != EXPECTED_VERSION: fail("version inválida")
    require_hash(aep["proof_hash"], "proof_hash")
    for field in ["intent", "authority", "policy", "execution", "evidence_ref", "verifier"]:
        if not isinstance(aep[field], dict): fail(f"{field} deve ser objeto")
    if aep["intent"].get("action") != "verify_automation": fail("intent inválido")
    pol = aep["policy"]
    if "id" not in pol or "version" not in pol: fail("policy sem id/version")
    require_hash(pol.get("policy_hash"), "policy.policy_hash")
    if "run_id" not in aep["execution"] or "commit" not in aep["execution"]: fail("execution inválida")
    ref = aep["evidence_ref"]
    if ref.get("artifact") != "evidence.json": fail("evidence_ref.artifact inválido")
    if ref.get("status") != "ok": fail("evidence_ref.status != ok")
    require_hash(ref.get("legacy_file_hash"), "evidence_ref.legacy_file_hash")
    files = ref.get("files")
    if not isinstance(files, dict): fail("evidence_ref.files deve ser objeto")
    if set(files) != EXPECTED_FILES: fail("evidence_ref.files fora do contrato")
    for fn, dg in files.items():
        safe_path(fn); require_hash(dg, f"evidence_ref.files.{fn}")
    ver = aep["verifier"]
    if ver.get("name") != "verify_aep.py": fail("verifier.name inválido")
    require_hash(ver.get("sha256"), "verifier.sha256")

def get_verifier_info():
    return {"name": "verify_aep.py", "version": "0.1.1", "sha256": sha256(Path(__file__).read_bytes())}

def generate():
    legacy, legacy_path = load_legacy()
    before = legacy_path.read_bytes()
    validate_files(legacy["files"], context="na geração")
    validate_frozen_baseline(legacy["files"])
    policy_hash = sha256(canonical(POLICY_DOC))
    body = {
      "proof_type": "AEP", "version": EXPECTED_VERSION,
      "intent": {"action": "verify_automation", "inputs": sorted(list(legacy["files"].keys()))},
      "authority": {"actor": "xa-trust-verifier", "delegation": "github-actions",
                    "note": "Declaração apenas. Não comprova autorização do Actions nem autentica executor. Não substitui Ed25519."},
      "policy": {"id": POLICY_DOC["id"], "version": POLICY_DOC["version"], "policy_hash": policy_hash,
                 "note": "POLICY_DOCUMENT_INTEGRITY != POLICY_EXECUTION_PROOF"},
      "execution": {"run_id": os.getenv("GITHUB_RUN_ID", "local"), "commit": os.getenv("GITHUB_SHA", "local"), "workflow": "verify-global"},
      "evidence_ref": {"artifact": "evidence.json", "status": legacy["status"], "files": legacy["files"], "legacy_file_hash": sha256(before)},
      "verifier": get_verifier_info(),
      "frozen_baseline": FROZEN_BASELINE,
      "classification": {
        "LEGACY_MANIFEST_CONSISTENCY": "IMPLEMENTED IN SOURCE",
        "FROZEN_BASELINE_IDENTITY": "VERIFIED_WITHIN_DECLARED_LOCAL_VALIDATION",
        "JCS": "IMPLEMENTED IN SOURCE",
        "POLICY_DOCUMENT_BINDING": "IMPLEMENTED IN SOURCE",
        "VERIFIER_IDENTITY": "IMPLEMENTED IN SOURCE",
        "Ed25519": "NOT IMPLEMENTED",
        "AUTHORITY_VERIFICATION": "NOT IMPLEMENTED",
        "INTEROPERABILITY": "NOT ESTABLISHED"
      },
      "disclaimer": "Logical envelope only. verifier.sha256 identifica o arquivo, proof_hash protege integridade. Nenhum substitui assinatura Ed25519."
    }
    proof_hash = sha256(canonical(body))
    aep = {**body, "proof_hash": proof_hash}
    Path("evidence_aep.json").write_text(json.dumps(aep, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    if legacy_path.read_bytes() != before:
        raise RuntimeError("LEGACY_ARTIFACT_MUTATED")
    print(f"GENERATE OK: {proof_hash} | FROZEN_BASELINE_IDENTITY OK")

def verify():
    if not Path("evidence_aep.json").is_file(): fail("evidence_aep.json não encontrado")
    data = load_json_utf8(Path("evidence_aep.json"))
    validate_structure(data)
    stored = data["proof_hash"]
    check = {k: v for k, v in data.items() if k != "proof_hash"}
    if sha256(canonical(check)) != stored: fail("proof_hash quebrou")
    if check["verifier"] != get_verifier_info():
        fail("VERIFIER_IDENTITY_MISMATCH")
    if check["policy"]["policy_hash"] != sha256(canonical(POLICY_DOC)): fail("policy_hash divergente")
    if check["evidence_ref"]["legacy_file_hash"] != sha256(Path("evidence.json").read_bytes()): fail("vínculo legado quebrou")
    validate_files(check["evidence_ref"]["files"], context="na verificação")
    validate_frozen_baseline(check["evidence_ref"]["files"])
    legacy, _ = load_legacy()
    if legacy["files"] != check["evidence_ref"]["files"]: fail("evidence.json divergente do evidence_ref")
    print("LOGICAL INTEGRITY CHECK: PASS - FROZEN_BASELINE_IDENTITY OK")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    try:
        if cmd == "generate": generate(); verify()
        elif cmd == "verify": verify()
        else: fail(f"Comando inválido: {cmd}")
    except (ValueError, OSError, RuntimeError) as e:
        print(f"FAIL: {e}"); sys.exit(1)
    except Exception as e:
        print(f"FAIL UNEXPECTED: {type(e).__name__}: {e}"); sys.exit(1)