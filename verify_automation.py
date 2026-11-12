verify_automation.py


import os, sys, json, hashlib, datetime
import rfc8785

def write_evidence(evidence):
    payload = rfc8785.dumps(evidence)
    evidence["sha256"] = hashlib.sha256(payload).hexdigest()
    report = json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False)
    open("evidence.json", "w", encoding="utf-8").write(report + "\n")
    print(report)

def base():
    return {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "repo": os.environ.get("GITHUB_REPOSITORY", "local/xa-trust-verifier"),
        "ci_system": "github-actions",
        "verifier": "xa-trust-azure-state-verifier",
        "verifier_version": "1.0.0",
        "canonicalization": "RFC8785-JCS",
        "mode": "MOCK - sem Azure",
    }

disable_local_auth = True
public_access = "Disabled"
sku = "Basic"
public_disabled = public_access is False or str(public_access).lower() == "disabled"
e = base()
e.update({
    "status": "QUERY_OK",
    "resource_id": "/subscriptions/mock/resourceGroups/example-resources/providers/Microsoft.Automation/automationAccounts/myAccount",
    "disableLocalAuth": disable_local_auth,
    "publicNetworkAccess": public_access,
    "sku": sku,
    "checks": {
        "disableLocalAuth_is_True": disable_local_auth is True,
        "publicNetworkAccess_is_Disabled": public_disabled,
        "sku_is_Basic": sku == "Basic",
    }
})
e["all_passed"] = all(e["checks"].values())
write_evidence(e)
sys.exit(0 if e["all_passed"] else 1)

