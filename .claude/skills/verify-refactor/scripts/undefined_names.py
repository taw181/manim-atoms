"""Names a module uses but never defines or imports, hidden by star imports.

    uv run --with pyflakes python undefined_names.py

Every module star-imports manim and a style module, so pyflakes can only say
a name "may be undefined, or defined from star imports". This imports each
module and checks those names against its real namespace: anything still
missing is genuinely undefined -- typically a function moved to another
module without its import following it, or a style constant moved to a
style the module doesn't see. Also lists explicit imports left unused.
Exits 1 if anything is undefined, or a module fails to import.
"""

import importlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "-C", str(Path(__file__).parent), "rev-parse",
                            "--show-toplevel"], capture_output=True, text=True).stdout.strip())
PACKAGE = ROOT / "src" / "manim_atoms"
bad = 0
for path in sorted(PACKAGE.rglob("*.py")):
    if path.name == "__init__.py":
        continue
    module = "manim_atoms." + ".".join(path.relative_to(PACKAGE).with_suffix("").parts)
    report = subprocess.run([sys.executable, "-m", "pyflakes", str(path)],
                            capture_output=True, text=True).stdout
    try:
        namespace = importlib.import_module(module)
    except Exception as error:  # noqa: BLE001 -- any failure to import is the finding
        print(f"IMPORT FAILS {module}: {error!r}")
        bad += 1
        continue
    for line in report.splitlines():
        name = (re.search(r"'(\w+)' may be undefined", line)
                or re.search(r"undefined name '(\w+)'", line))
        if name and not hasattr(namespace, name.group(1)):
            print(line)
            bad += 1
        elif "imported but unused" in line:
            print(line)
print(f"undefined: {bad}")
sys.exit(1 if bad else 0)
