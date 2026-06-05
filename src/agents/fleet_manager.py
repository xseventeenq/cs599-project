"""
资源调度 Agent

负责匹配无人机能力、位置，分配任务给合适的无人机。
"""

import logging
import random
from typing import Any, Dict, List, Optional

try:
    from langchain_core.language_models import BaseChatModel
except Exception:  # LangChain is optional for the deterministic demo
    BaseChatModel = object


class FleetManagerAgent:
    """资源调度 Agent，负责无人机任务分配"""
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化资源调度 Agent
        
        Args:
            llm: 语言模型实例
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        
        # 模拟无人机机队
        self.drone_fleet = self._initialize_drone_fleet()
    
    def _initialize_drone_fleet(self) -> List[Dict[str, Any]]:
        """
        初始化无人机机队
        
        Returns:
            无人机列表
        """
        fleet = [
            {
                "id": "drone_001",
                "type": "救援无人机",
                "capabilities": ["物资投放", "人员救援", "区域侦察"],
                "max_payload": 10.0,  # 最大载重（千克）
                "max_flight_time": 60,  # 最大飞行时间（分钟）
                "max_speed": 15.0,  # 最大速度（米/秒）
                "battery_level": 1.0,  # 电池电量
                "current_position": (0, 0),  # 当前位置
                "status": "available",
                "special_equipment": ["医疗包", "救生绳"]
            },
            {
                "id": "drone_002",
                "type": "配送无人机",
                "capabilities": ["物资配送", "路径规划"],
                "max_payload": 5.0,
                "max_flight_time": 45,
                "max_speed": 20.0,
                "battery_level": 0.9,
                "current_position": (10, 10),
                "status": "available",
                "special_equipment": ["配送箱"]
            },
            {
                "id": "drone_003",
                "type": "侦察无人机",
                "capabilities": ["区域侦察", "实时监控", "图像传输"],
                "max_payload": 2.0,
                "max_flight_time": 90,
                "max_speed": 12.0,
                "battery_level": 0.8,
                "current_position": (-5, 5),
                "status": "available",
                "special_equipment": ["高清摄像头", "红外传感器"]
            },
            {
                "id": "drone_004",
                "type": "通用无人机",
                "capabilities": ["物资配送", "区域侦察", "简单救援"],
                "max_payload": 3.0,
                "max_flight_time": 50,
                "max_speed": 18.0,
                "battery_level": 0.7,
                "current_position": (5, -5),
                "status": "available",
                "special_equipment": ["基础工具包"]
            },
            {
                "id": "drone_005",
                "type": "重型无人机",
                "capabilities": ["重型物资运输", "大型设备吊装"],
                "max_payload": 20.0,
                "max_flight_time": 40,
                "max_speed": 10.0,
                "battery_level": 0.95,
                "current_position": (0, -10),
                "status": "available",
                "special_equipment": ["重型吊臂"]
            }
        ]
        
        return fleet
    
    def allocate(self, analyzed_mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        分配任务给无人机
        
        Args:
            analyzed_mission: 分析后的任务描述
            
        Returns:
            无人机分配方案
        """
        self.logger.info("开始资源调度")
        
        # 1. 筛选可用无人机
        available_drones = self._filter_available_drones(analyzed_mission)
        
        # 2. 匹配能力需求
        matched_drones = self._match_capabilities(analyzed_mission, available_drones)
        
        # 3. 优化分配
        optimized_allocation = self._optimize_allocation(analyzed_mission, matched_drones)
        
        # 4. 生成调度方案
        allocation_plan = {
            "mission_id": analyzed_mission.get("original_mission", {}).get("id", "unknown"),
            "mission_type": analyzed_mission.get("type", "unknown"),
            "allocated_drones": optimized_allocation,
            "total_drones": len(optimized_allocation),
            "estimated_duration": self._estimate_total_duration(optimized_allocation),
            "resource_utilization": self._calculate_resource_utilization(optimized_allocation),
            "backup_drones": self._select_backup_drones(analyzed_mission, optimized_allocation)
        }
        
        self.logger.info(f"资源调度完成，分配了 {len(optimized_allocation)} 架无人机")
        return allocation_plan
    
    def _filter_available_drones(self, analyzed_mission: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        筛选可用无人机
        
        Args:
            analyzed_mission: 任务描述
            
        Returns:
            可用无人机列表
        """
        available = []
        
        for drone in self.drone_fleet:
            if drone["status"] == "available" and drone["battery_level"] > 0.3:
                # 检查电池是否满足任务需求
                battery_requirement = analyzed_mission.get("resource_needs", {}).get("battery_requirement", 0.7)
                if drone["battery_level"] >= battery_requirement:
                    available.append(drone)
        
        return available
    
    def _match_capabilities(self, analyzed_mission: Dict[str, Any], available_drones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        匹配能力需求
        
        Args:
            analyzed_mission: 任务描述
            available_drones: 可用无人机列表
            
        Returns:
            匹配的无人机列表
        """
        mission_type = analyzed_mission.get("type", "unknown")
        required_capabilities = self._get_required_capabilities(mission_type)
        
        matched = []
        for drone in available_drones:
            drone_capabilities = set(drone["capabilities"])
            required_set = set(required_capabilities)
            
            # 计算能力匹配度
            if required_set.issubset(drone_capabilities):
                # 完全匹配
                drone["match_score"] = 1.0
                matched.append(drone)
            elif drone_capabilities.intersection(required_set):
                # 部分匹配
                match_ratio = len(drone_capabilities.intersection(required_set)) / len(required_set)
                drone["match_score"] = match_ratio
                matched.append(drone)
        
        # 按匹配度排序
        matched.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return matched
    
    def _get_required_capabilities(self, mission_type: str) -> List[str]:
        """
        获取任务类型所需的能力
        
        Args:
            mission_type: 任务类型
            
        Returns:
            所需能力列表
        """
        capabilities_map = {
            "disaster_rescue": ["区域侦察", "物资投放", "人员救援"],
            "delivery": ["物资配送", "路径规划"],
            "surveillance": ["区域侦察", "实时监控"],
            "agriculture": ["喷洒作业", "作物监测"],
            "entertainment": ["编队飞行", "灯光控制"]
        }
        
        return capabilities_map.get(mission_type, ["基础操作"])
    
    def _optimize_allocation(self, analyzed_mission: Dict[str, Any], matched_drones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        优化分配
        
        Args:
            analyzed_mission: 任务描述
            matched_drones: 匹配的无人机列表
            
        Returns:
            优化后的分配列表
        """
        min_drones = analyzed_mission.get("resource_needs", {}).get("min_drones", 1)
        max_drones = analyzed_mission.get("resource_needs", {}).get("max_drones", 3)
        
        # 选择最佳无人机
        selected = []
        total_payload = 0
        total_flight_time = 0
        
        required_payload = self._calculate_total_payload(analyzed_mission)
        # 这里采用“至少满足任务需求”的调度思路：优先选择能力匹配度高的无人机，
        # 直到达到最小数量要求或累计载重覆盖任务需求。
        for drone in matched_drones:
            if len(selected) >= max_drones:
                break
            selected.append(drone)
            total_payload += drone["max_payload"]
            total_flight_time = max(total_flight_time, drone["max_flight_time"])
            if len(selected) >= min_drones and total_payload >= required_payload:
                break
        
        # 确保满足最小数量要求
        if len(selected) < min_drones and len(matched_drones) >= min_drones:
            # 补充到最小数量
            for drone in matched_drones:
                if drone not in selected and len(selected) < min_drones:
                    selected.append(drone)
        
        # 为每架无人机分配具体任务
        for i, drone in enumerate(selected):
            drone["assigned_task"] = self._assign_specific_task(analyzed_mission, i, len(selected))
            drone["estimated_duration"] = self._estimate_drone_duration(drone, analyzed_mission)
        
        return selected
    
    def _calculate_total_payload(self, analyzed_mission: Dict[str, Any]) -> float:
        """
        计算总载重需求
        
        Args:
            analyzed_mission: 任务描述
            
        Returns:
            总载重需求（千克）
        """
        base_payload = analyzed_mission.get("resource_needs", {}).get("payload_capacity", 2.0)
        num_objects = len(analyzed_mission.get("objects", []))
        
        return base_payload * (1 + num_objects * 0.1)
    
    def _assign_specific_task(self, analyzed_mission: Dict[str, Any], drone_index: int, total_drones: int) -> str:
        """
        为无人机分配具体任务
        
        Args:
            analyzed_mission: 任务描述
            drone_index: 无人机索引
            total_drones: 总无人机数量
            
        Returns:
            具体任务描述
        """
        mission_type = analyzed_mission.get("type", "unknown")
        subtasks = analyzed_mission.get("subtasks", [])
        
        if not subtasks:
            return "执行通用任务"
        
        # 根据无人机类型和任务类型分配任务
        task_assignments = {
            "disaster_rescue": {
                0: "区域侦察与目标定位",
                1: "医疗物资投放",
                2: "人员救援与撤离"
            },
            "delivery": {
                0: "货物装载与配送",
                1: "路径监控与协调"
            },
            "surveillance": {
                0: "区域A监控",
                1: "区域B监控",
                2: "异常情况报告"
            }
        }
        
        if mission_type in task_assignments:
            return task_assignments[mission_type].get(drone_index, f"执行子任务{drone_index + 1}")
        
        # 默认分配
        if drone_index < len(subtasks):
            return subtasks[drone_index].get("name", f"执行子任务{drone_index + 1}")
        
        return "执行辅助任务"
    
    def _estimate_drone_duration(self, drone: Dict[str, Any], analyzed_mission: Dict[str, Any]) -> int:
        """
        估算单架无人机任务持续时间
        
        Args:
            drone: 无人机信息
            analyzed_mission: 任务描述
            
        Returns:
            估计持续时间（分钟）
        """
        base_duration = analyzed_mission.get("estimated_duration", 30)
        
        # 根据无人机性能调整
        performance_factor = (drone["max_speed"] / 15.0) * (drone["max_flight_time"] / 60.0)
        adjusted_duration = base_duration / performance_factor
        
        return int(adjusted_duration)
    
    def _estimate_total_duration(self, allocated_drones: List[Dict[str, Any]]) -> int:
        """
        估算总任务持续时间
        
        Args:
            allocated_drones: 分配的无人机列表
            
        Returns:
            总持续时间（分钟）
        """
        if not allocated_drones:
            return 0
        
        # 取最长的任务持续时间
        max_duration = max(drone.get("estimated_duration", 0) for drone in allocated_drones)
        
        # 考虑协调开销
        coordination_overhead = len(allocated_drones) * 2  # 每架无人机2分钟协调时间
        
        return max_duration + coordination_overhead
    
    def _calculate_resource_utilization(self, allocated_drones: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算资源利用率
        
        Args:
            allocated_drones: 分配的无人机列表
            
        Returns:
            资源利用率字典
        """
        if not allocated_drones:
            return {"drone_utilization": 0.0, "payload_utilization": 0.0, "energy_utilization": 0.0}
        
        # 无人机利用率
        total_drones = len(self.drone_fleet)
        drone_utilization = len(allocated_drones) / total_drones
        
        # 载重利用率
        total_payload_capacity = sum(drone["max_payload"] for drone in allocated_drones)
        used_payload = total_payload_capacity * 0.6  # 假设使用60%载重
        payload_utilization = used_payload / total_payload_capacity if total_payload_capacity > 0 else 0
        
        # 能量利用率
        total_energy = sum(drone["battery_level"] for drone in allocated_drones)
        used_energy = total_energy * 0.7  # 假设使用70%能量
        energy_utilization = used_energy / total_energy if total_energy > 0 else 0
        
        return {
            "drone_utilization": drone_utilization,
            "payload_utilization": payload_utilization,
            "energy_utilization": energy_utilization,
            "overall_utilization": (drone_utilization + payload_utilization + energy_utilization) / 3
        }
    
    def _select_backup_drones(self, analyzed_mission: Dict[str, Any], allocated_drones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        选择备用无人机
        
        Args:
            analyzed_mission: 任务描述
            allocated_drones: 已分配的无人机列表
            
        Returns:
            备用无人机列表
        """
        backup = []
        
        for drone in self.drone_fleet:
            if drone not in allocated_drones and drone["status"] == "available":
                # 检查是否适合作为备用
                if drone["battery_level"] > 0.5:
                    backup.append({
                        "id": drone["id"],
                        "type": drone["type"],
                        "reason": "备用无人机，可随时支援"
                    })
            
            if len(backup) >= 2:  # 最多选择2架备用
                break
        
        return backup