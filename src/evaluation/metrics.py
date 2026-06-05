from typing import Dict, Any


def calculate_success_rate(result: Dict[str, Any]) -> float:
    if result.get("status") != "success":
        return 0.0
    return result.get("metrics", {}).get("success_rate", 0.0)


def calculate_total_cost(result: Dict[str, Any]) -> float:
    return result.get("metrics", {}).get("total_cost", 0.0)


def calculate_average_risk(result: Dict[str, Any]) -> float:
    return result.get("metrics", {}).get("average_risk", 0.0)
