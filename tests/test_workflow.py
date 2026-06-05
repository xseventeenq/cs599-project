from src.main import UAVMissionAgent


def test_workflow_success():
    agent = UAVMissionAgent()
    result = agent.execute({
        "type": "disaster_rescue",
        "location": "测试区域",
        "priority": "high",
        "objects": ["受困人员"],
        "constraints": ["复杂地形"],
        "num_drones": 2,
    })
    assert result["status"] == "success"
    assert result["metrics"]["success_rate"] > 0
    assert result["plan"]["drone_allocation"]["total_drones"] >= 1
