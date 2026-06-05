"""
任务分析 Agent

负责解析用户输入的任务，分解任务，评估优先级，并生成结构化的任务描述。
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from langchain_core.language_models import BaseChatModel
except Exception:  # LangChain is optional for the deterministic demo
    BaseChatModel = object


class TaskAnalyzerAgent:
    """任务分析 Agent，负责任务解析和分解"""
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化任务分析 Agent
        
        Args:
            llm: 语言模型实例，如果为None则使用默认配置
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm  # 实际项目中会初始化LLM
        
        # 任务类型定义
        self.mission_types = {
            "disaster_rescue": "灾难救援",
            "delivery": "物资配送",
            "surveillance": "监控侦察",
            "agriculture": "农业作业",
            "entertainment": "娱乐表演"
        }
        
        # 优先级定义
        self.priorities = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "minimal": 1
        }
    
    def analyze(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析任务
        
        Args:
            mission: 原始任务描述
            
        Returns:
            分析后的结构化任务描述
        """
        self.logger.info(f"开始分析任务: {mission.get('type', 'unknown')}")
        
        # 1. 验证任务类型
        mission_type = mission.get("type", "unknown")
        if mission_type not in self.mission_types:
            self.logger.warning(f"未知任务类型: {mission_type}，使用默认类型")
            mission_type = "delivery"  # 默认类型
        
        # 2. 分析优先级
        priority = self._analyze_priority(mission)
        
        # 3. 分解任务
        subtasks = self._decompose_mission(mission)
        
        # 4. 评估约束条件
        constraints = self._evaluate_constraints(mission)
        
        # 5. 计算资源需求
        resource_needs = self._calculate_resource_needs(mission)
        
        # 生成结构化任务描述
        analyzed_mission = {
            "original_mission": mission,
            "type": mission_type,
            "type_name": self.mission_types[mission_type],
            "priority": priority,
            "priority_score": self.priorities[priority],
            "subtasks": subtasks,
            "constraints": constraints,
            "resource_needs": resource_needs,
            "location": mission.get("location", "未指定"),
            "objects": mission.get("objects", []),
            "num_drones_required": resource_needs.get("min_drones", 1),
            "estimated_duration": self._estimate_duration(mission, subtasks),
            "risk_assessment": self._assess_risks(mission)
        }
        
        self.logger.info(f"任务分析完成: 类型={mission_type}, 优先级={priority}")
        return analyzed_mission
    
    def _analyze_priority(self, mission: Dict[str, Any]) -> str:
        """
        分析任务优先级
        
        Args:
            mission: 任务描述
            
        Returns:
            优先级等级
        """
        # 优先级评估规则
        priority_indicators = {
            "critical": ["紧急", "立即", "生命危险", "critical", "emergency"],
            "high": ["高优先级", "重要", "high", "urgent"],
            "medium": ["中等", "一般", "medium", "normal"],
            "low": ["低优先级", "不紧急", "low"],
            "minimal": ["最小", "可选", "minimal", "optional"]
        }
        
        # 检查任务描述中的优先级指示词
        mission_text = str(mission).lower()
        
        for priority, indicators in priority_indicators.items():
            for indicator in indicators:
                if indicator in mission_text:
                    return priority
        
        # 默认优先级
        return "medium"
    
    def _decompose_mission(self, mission: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        分解任务
        
        Args:
            mission: 任务描述
            
        Returns:
            子任务列表
        """
        mission_type = mission.get("type", "unknown")
        subtasks = []
        
        if mission_type == "disaster_rescue":
            subtasks = [
                {"id": 1, "name": "区域侦察", "duration": 10, "required": True},
                {"id": 2, "name": "目标定位", "duration": 15, "required": True},
                {"id": 3, "name": "物资投放", "duration": 20, "required": True},
                {"id": 4, "name": "人员救援", "duration": 30, "required": True},
                {"id": 5, "name": "安全撤离", "duration": 15, "required": True}
            ]
        elif mission_type == "delivery":
            subtasks = [
                {"id": 1, "name": "货物装载", "duration": 5, "required": True},
                {"id": 2, "name": "路径规划", "duration": 10, "required": True},
                {"id": 3, "name": "飞行配送", "duration": 25, "required": True},
                {"id": 4, "name": "货物卸载", "duration": 5, "required": True}
            ]
        elif mission_type == "surveillance":
            subtasks = [
                {"id": 1, "name": "区域划分", "duration": 10, "required": True},
                {"id": 2, "name": "巡逻规划", "duration": 15, "required": True},
                {"id": 3, "name": "实时监控", "duration": 40, "required": True},
                {"id": 4, "name": "异常报告", "duration": 5, "required": False}
            ]
        else:
            subtasks = [
                {"id": 1, "name": "任务准备", "duration": 10, "required": True},
                {"id": 2, "name": "任务执行", "duration": 30, "required": True},
                {"id": 3, "name": "任务完成", "duration": 10, "required": True}
            ]
        
        return subtasks
    
    def _evaluate_constraints(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估约束条件
        
        Args:
            mission: 任务描述
            
        Returns:
            约束条件字典
        """
        constraints = mission.get("constraints", [])
        
        evaluated_constraints = {
            "weather": False,
            "terrain": False,
            "time_limit": False,
            "energy": False,
            "communication": False
        }
        
        # 检查约束类型
        for constraint in constraints:
            constraint_lower = constraint.lower()
            if "天气" in constraint_lower or "weather" in constraint_lower:
                evaluated_constraints["weather"] = True
            elif "地形" in constraint_lower or "terrain" in constraint_lower:
                evaluated_constraints["terrain"] = True
            elif "时间" in constraint_lower or "time" in constraint_lower:
                evaluated_constraints["time_limit"] = True
            elif "能量" in constraint_lower or "energy" in constraint_lower:
                evaluated_constraints["energy"] = True
            elif "通信" in constraint_lower or "communication" in constraint_lower:
                evaluated_constraints["communication"] = True
        
        # 添加时间限制
        if "time_limit" in mission:
            evaluated_constraints["time_limit"] = True
            evaluated_constraints["max_duration"] = mission["time_limit"]
        
        return evaluated_constraints
    
    def _calculate_resource_needs(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算资源需求
        
        Args:
            mission: 任务描述
            
        Returns:
            资源需求字典
        """
        mission_type = mission.get("type", "unknown")
        num_objects = len(mission.get("objects", []))
        
        # 基于任务类型和对象数量计算无人机数量
        if mission_type == "disaster_rescue":
            min_drones = max(2, num_objects + 1)
            max_drones = min_drones + 2
        elif mission_type == "delivery":
            min_drones = max(1, num_objects // 2 + 1)
            max_drones = min_drones + 1
        elif mission_type == "surveillance":
            min_drones = 2
            max_drones = 4
        else:
            min_drones = 1
            max_drones = 3
        
        # 检查用户指定的无人机数量
        specified_drones = mission.get("num_drones", 0)
        if specified_drones > 0:
            min_drones = max(min_drones, specified_drones)
            max_drones = max(max_drones, specified_drones)
        
        return {
            "min_drones": min_drones,
            "max_drones": max_drones,
            "drone_types": self._select_drone_types(mission_type),
            "battery_requirement": self._estimate_battery(mission_type),
            "payload_capacity": self._estimate_payload(mission_type, num_objects)
        }
    
    def _select_drone_types(self, mission_type: str) -> List[str]:
        """
        选择无人机类型
        
        Args:
            mission_type: 任务类型
            
        Returns:
            无人机类型列表
        """
        drone_types = {
            "disaster_rescue": ["救援无人机", "医疗物资无人机"],
            "delivery": ["配送无人机"],
            "surveillance": ["侦察无人机", "监控无人机"],
            "agriculture": ["农业无人机"],
            "entertainment": ["表演无人机"]
        }
        
        return drone_types.get(mission_type, ["通用无人机"])
    
    def _estimate_battery(self, mission_type: str) -> float:
        """
        估算电池需求
        
        Args:
            mission_type: 任务类型
            
        Returns:
            电池需求百分比
        """
        battery_needs = {
            "disaster_rescue": 0.9,  # 需要高续航
            "delivery": 0.7,
            "surveillance": 0.8,
            "agriculture": 0.85,
            "entertainment": 0.6
        }
        
        return battery_needs.get(mission_type, 0.75)
    
    def _estimate_payload(self, mission_type: str, num_objects: int) -> float:
        """
        估算载重需求
        
        Args:
            mission_type: 任务类型
            num_objects: 对象数量
            
        Returns:
            载重需求（千克）
        """
        base_payload = {
            "disaster_rescue": 5.0,
            "delivery": 2.0,
            "surveillance": 1.0,
            "agriculture": 10.0,
            "entertainment": 0.5
        }
        
        base = base_payload.get(mission_type, 2.0)
        return base * (1 + num_objects * 0.2)
    
    def _estimate_duration(self, mission: Dict[str, Any], subtasks: List[Dict[str, Any]]) -> int:
        """
        估算任务持续时间
        
        Args:
            mission: 任务描述
            subtasks: 子任务列表
            
        Returns:
            估计持续时间（分钟）
        """
        total_duration = sum(task.get("duration", 0) for task in subtasks)
        
        # 考虑约束条件的影响
        constraints = mission.get("constraints", [])
        if constraints:
            total_duration *= 1.2  # 有约束时增加20%时间
        
        return int(total_duration)
    
    def _assess_risks(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估风险
        
        Args:
            mission: 任务描述
            
        Returns:
            风险评估字典
        """
        mission_type = mission.get("type", "unknown")
        constraints = mission.get("constraints", [])
        
        # 基础风险评估
        base_risks = {
            "disaster_rescue": {"level": "high", "score": 0.7},
            "delivery": {"level": "medium", "score": 0.3},
            "surveillance": {"level": "low", "score": 0.2},
            "agriculture": {"level": "low", "score": 0.1},
            "entertainment": {"level": "low", "score": 0.15}
        }
        
        risk = base_risks.get(mission_type, {"level": "medium", "score": 0.4})
        
        # 根据约束条件调整风险
        risk_adjustments = {
            "weather": 0.2,
            "terrain": 0.15,
            "time_limit": 0.1,
            "energy": 0.1,
            "communication": 0.15
        }
        
        for constraint in constraints:
            constraint_lower = constraint.lower()
            for key, adjustment in risk_adjustments.items():
                if key in constraint_lower:
                    risk["score"] += adjustment
        
        # 确保风险分数在0-1之间
        risk["score"] = min(max(risk["score"], 0), 1)
        
        # 更新风险等级
        if risk["score"] > 0.7:
            risk["level"] = "critical"
        elif risk["score"] > 0.5:
            risk["level"] = "high"
        elif risk["score"] > 0.3:
            risk["level"] = "medium"
        else:
            risk["level"] = "low"
        
        return risk