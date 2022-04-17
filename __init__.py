from pathlib import Path
import sys
module_path = Path(__file__).parent.resolve(strict=True).as_posix()

# append this submodule to sys path
sys.path.append(module_path)