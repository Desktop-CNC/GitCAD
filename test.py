import subprocess
from pathlib import Path as path

result = subprocess.run(["git", "push"], cwd= path.home() / "Documents" / "GitHub" / "GitCAD", check=False, capture_output=True, shell=True)

print(result.returncode)
print(result.stderr.decode()) 