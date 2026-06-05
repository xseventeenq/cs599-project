# API Spec：UAV-Mission-Agent

## 1. 核心接口

### `UAVMissionAgent.execute(mission)`
执行任务分配完整流程。

#### Request
```json
{
  "type": "disaster_rescue",
  "location": "城市A区域",
  "priority": "high",
  "objects": ["受困人员", "医疗物资"],
  "constraints": ["恶劣天气", "复杂地形"],
  "num_drones": 3,
  "max_distance": 50.0,
  "time_limit": 60
}
```

#### Response
```json
{
  "status": "success",
  "plan": {
    "analyzed_mission": {},
    "drone_allocation": {},
    "route_plan": {},
    "monitoring": {}
  },
  "metrics": {
    "success_rate": 0.85,
    "total_cost": 1000.0,
    "average_risk": 0.3,
    "collaboration_efficiency": 0.0
  }
}
```

## 2. Agent 内部接口

### TaskAnalyzerAgent.analyze(mission)
输出结构化任务信息。

### FleetManagerAgent.allocate(analyzed_mission)
输出无人机分配方案。

### RoutePlannerAgent.plan(allocation_plan)
输出飞行路径和风险缓解方案。

### MonitorAgent.monitor(route_plan)
输出模拟执行日志、异常和建议。

## 3. 错误处理
当执行失败时，返回：
```json
{
  "status": "failed",
  "error": "错误信息"
}
```
