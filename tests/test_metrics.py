from src.evaluation.metrics import calculate_success_rate, calculate_total_cost, calculate_average_risk


def test_metrics_helpers():
    result = {"status": "success", "metrics": {"success_rate": 0.9, "total_cost": 10, "average_risk": 0.2}}
    assert calculate_success_rate(result) == 0.9
    assert calculate_total_cost(result) == 10
    assert calculate_average_risk(result) == 0.2
