import json
from pathlib import Path
from typing import List, Dict, Any

from src.main import UAVMissionAgent


def run_benchmark(case_file: str = "examples/mission_cases.json") -> List[Dict[str, Any]]:
    cases = json.loads(Path(case_file).read_text(encoding="utf-8"))
    agent = UAVMissionAgent()
    return [agent.execute(case) for case in cases]


if __name__ == "__main__":
    results = run_benchmark()
    print(json.dumps(results, ensure_ascii=False, indent=2))
