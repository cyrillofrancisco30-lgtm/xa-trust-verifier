
import subprocess, sys
f = sys.argv[1]
r = subprocess.run(["ots", "verify", f + ".ots"], capture_output=True, text=True)
print(r.stdout)
print(r.stderr)

