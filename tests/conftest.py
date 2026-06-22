import sys
from pathlib import Path

# 将项目根目录加入 sys.path，解决 from src.xxx 的导入问题
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
