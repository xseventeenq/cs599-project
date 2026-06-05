"""
路径规划 Agent

负责使用GNN优化路径，进行避障规划，生成最优飞行路径。
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

try:
    from langchain_core.language_models import BaseChatModel
except Exception:  # LangChain is optional for the deterministic demo
    BaseChatModel = object


class RoutePlannerAgent:
    """路径规划 Agent，负责路径优化和避障"""
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化路径规划 Agent
        
        Args:
            llm: 语言模型实例
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        
        # 模拟地图和障碍物
        self.map_size = (100, 100)  # 地图尺寸
        self.obstacles = self._generate_obstacles()
        self.no_fly_zones = self._generate_no_fly_zones()
    
    def _generate_obstacles(self) -> List[Dict[str, Any]]:
        """
        生成模拟障碍物
        
        Returns:
            障碍物列表
        """
        obstacles = [
            {"id": "obs_001", "type": "building", "position": (20, 30), "size": (10, 10)},
            {"id": "obs_002", "type": "tower", "position": (50, 50), "size": (5, 5)},
            {"id": "obs_003", "type": "mountain", "position": (70, 20), "size": (15, 15)},
            {"id": "obs_004", "type": "river", "position": (30, 70), "size": (20, 5)},
            {"id": "obs_005", "type": "power_line", "position": (60, 80), "size": (3, 30)}
        ]
        
        return obstacles
    
    def _generate_no_fly_zones(self) -> List[Dict[str, Any]]:
        """
        生成禁飞区
        
        Returns:
            禁飞区列表
        """
        no_fly_zones = [
            {"id": "nfz_001", "type": "airport", "center": (10, 90), "radius": 15},
            {"id": "nfz_002", "type": "military", "center": (90, 10), "radius": 20},
            {"id": "nfz_003", "type": "government", "center": (50, 50), "radius": 10}
        ]
        
        return no_fly_zones
    
    def plan(self, allocation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        规划路径
        
        Args:
            allocation_plan: 无人机分配方案
            
        Returns:
            路径规划方案
        """
        self.logger.info("开始路径规划")
        
        allocated_drones = allocation_plan.get("allocated_drones", [])
        route_plans = []
        
        # 为每架无人机规划路径
        for drone in allocated_drones:
            drone_route = self._plan_drone_route(drone, allocation_plan)
            route_plans.append(drone_route)
        
        # 生成全局路径规划
        global_route_plan = self._generate_global_plan(route_plans)
        
        # 计算总体指标
        overall_metrics = self._calculate_overall_metrics(route_plans)
        
        route_plan = {
            "mission_id": allocation_plan.get("mission_id", "unknown"),
            "drone_routes": route_plans,
            "global_plan": global_route_plan,
            "overall_metrics": overall_metrics,
            "coordination_plan": self._generate_coordination_plan(route_plans),
            "risk_mitigation": self._generate_risk_mitigation_plan(route_plans)
        }
        
        self.logger.info(f"路径规划完成，规划了 {len(route_plans)} 条路径")
        return route_plan
    
    def _plan_drone_route(self, drone: Dict[str, Any], allocation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        为单架无人机规划路径
        
        Args:
            drone: 无人机信息
            allocation_plan: 分配方案
            
        Returns:
            无人机路径规划
        """
        drone_id = drone.get("id", "unknown")
        assigned_task = drone.get("assigned_task", "执行任务")
        
        self.logger.info(f"为无人机 {drone_id} 规划路径，任务: {assigned_task}")
        
        # 生成起点和终点
        start_point = drone.get("current_position", (0, 0))
        end_point = self._determine_end_point(assigned_task, start_point)
        
        # 使用简化A*算法规划路径
        path = self._astar_pathfinding(start_point, end_point)
        
        # 路径平滑处理
        smoothed_path = self._smooth_path(path)
        
        # 避障检查
        safe_path = self._check_obstacle_avoidance(smoothed_path)
        
        # 计算路径指标
        path_metrics = self._calculate_path_metrics(safe_path, drone)
        
        drone_route = {
            "drone_id": drone_id,
            "drone_type": drone.get("type", "unknown"),
            "task": assigned_task,
            "start_point": start_point,
            "end_point": end_point,
            "path": safe_path,
            "path_length": path_metrics["total_distance"],
            "estimated_time": path_metrics["estimated_time"],
            "energy_consumption": path_metrics["energy_consumption"],
            "risk_level": path_metrics["risk_level"],
            "waypoints": self._extract_waypoints(safe_path),
            "obstacles_avoided": path_metrics["obstacles_avoided"],
            "altitude_profile": self._generate_altitude_profile(safe_path)
        }
        
        return drone_route
    
    def _determine_end_point(self, task: str, start_point: Tuple[int, int]) -> Tuple[int, int]:
        """
        确定终点
        
        Args:
            task: 任务描述
            start_point: 起点
            
        Returns:
            终点坐标
        """
        # 基于任务类型确定终点
        if "侦察" in task or "监控" in task:
            # 侦察任务：去往地图中心区域
            return (50, 50)
        elif "救援" in task:
            # 救援任务：去往地图边缘区域
            return (80, 20)
        elif "配送" in task:
            # 配送任务：去往指定位置
            return (30, 70)
        else:
            # 默认：去往地图中心
            return (50, 50)
    
    def _astar_pathfinding(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        A*路径规划算法
        
        Args:
            start: 起点
            end: 终点
            
        Returns:
            路径点列表
        """
        # 简化实现：使用直线路径加避障调整
        path = []
        
        # 生成直线路径
        x1, y1 = start
        x2, y2 = end
        
        # 计算步数
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy)
        
        if steps == 0:
            return [start]
        
        # 生成路径点
        for i in range(steps + 1):
            t = i / steps
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            path.append((x, y))
        
        return path
    
    def _smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        路径平滑处理
        
        Args:
            path: 原始路径
            
        Returns:
            平滑后的路径
        """
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        
        for i in range(1, len(path) - 1):
            # 使用简单的移动平均平滑
            prev_point = path[i - 1]
            curr_point = path[i]
            next_point = path[i + 1]
            
            # 计算平滑点
            smooth_x = int((prev_point[0] + curr_point[0] + next_point[0]) / 3)
            smooth_y = int((prev_point[1] + curr_point[1] + next_point[1]) / 3)
            
            smoothed.append((smooth_x, smooth_y))
        
        smoothed.append(path[-1])
        
        return smoothed
    
    def _check_obstacle_avoidance(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        避障检查
        
        Args:
            path: 原始路径
            
        Returns:
            避障后的路径
        """
        safe_path = []
        
        for point in path:
            # 检查是否在障碍物内
            if self._is_in_obstacle(point):
                # 如果在障碍物内，寻找附近安全点
                safe_point = self._find_safe_nearby_point(point)
                safe_path.append(safe_point)
            elif self._is_in_no_fly_zone(point):
                # 如果在禁飞区内，寻找替代点
                safe_point = self._find_alternative_point(point)
                safe_path.append(safe_point)
            else:
                safe_path.append(point)
        
        return safe_path
    
    def _is_in_obstacle(self, point: Tuple[int, int]) -> bool:
        """
        检查点是否在障碍物内
        
        Args:
            point: 检查点
            
        Returns:
            是否在障碍物内
        """
        x, y = point
        
        for obstacle in self.obstacles:
            obs_x, obs_y = obstacle["position"]
            obs_width, obs_height = obstacle["size"]
            
            if (obs_x <= x <= obs_x + obs_width and 
                obs_y <= y <= obs_y + obs_height):
                return True
        
        return False
    
    def _is_in_no_fly_zone(self, point: Tuple[int, int]) -> bool:
        """
        检查点是否在禁飞区内
        
        Args:
            point: 检查点
            
        Returns:
            是否在禁飞区内
        """
        x, y = point
        
        for zone in self.no_fly_zones:
            center_x, center_y = zone["center"]
            radius = zone["radius"]
            
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= radius:
                return True
        
        return False
    
    def _find_safe_nearby_point(self, point: Tuple[int, int]) -> Tuple[int, int]:
        """
        寻找附近安全点
        
        Args:
            point: 原始点
            
        Returns:
            安全点坐标
        """
        x, y = point
        
        # 尝试向不同方向移动
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx * 5, y + dy * 5
            if (0 <= new_x < self.map_size[0] and 
                0 <= new_y < self.map_size[1] and
                not self._is_in_obstacle((new_x, new_y)) and
                not self._is_in_no_fly_zone((new_x, new_y))):
                return (new_x, new_y)
        
        # 如果找不到安全点，返回原始点
        return point
    
    def _find_alternative_point(self, point: Tuple[int, int]) -> Tuple[int, int]:
        """
        寻找替代点
        
        Args:
            point: 原始点
            
        Returns:
            替代点坐标
        """
        x, y = point
        
        # 尝试移动到禁飞区边缘
        for zone in self.no_fly_zones:
            center_x, center_y = zone["center"]
            radius = zone["radius"]
            
            # 计算从中心到点的方向
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            if distance > 0:
                # 移动到禁飞区外
                new_x = center_x + int(radius * 1.2 * dx / distance)
                new_y = center_y + int(radius * 1.2 * dy / distance)
                
                # 确保在地图范围内
                new_x = max(0, min(new_x, self.map_size[0] - 1))
                new_y = max(0, min(new_y, self.map_size[1] - 1))
                
                return (new_x, new_y)
        
        return point
    
    def _calculate_path_metrics(self, path: List[Tuple[int, int]], drone: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算路径指标
        
        Args:
            path: 路径点列表
            drone: 无人机信息
            
        Returns:
            路径指标字典
        """
        total_distance = 0.0
        obstacles_avoided = 0
        
        # 计算总距离
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            total_distance += distance
        
        # 估算时间（基于无人机速度）
        speed = drone.get("max_speed", 15.0)  # 米/秒
        estimated_time = total_distance / speed / 60  # 转换为分钟
        
        # 计算能量消耗
        energy_consumption = total_distance * 0.01  # 简化计算
        
        # 评估风险等级
        risk_level = self._assess_path_risk(path)
        
        # 统计避障次数
        for point in path:
            if self._is_in_obstacle(point) or self._is_in_no_fly_zone(point):
                obstacles_avoided += 1
        
        return {
            "total_distance": total_distance,
            "estimated_time": estimated_time,
            "energy_consumption": energy_consumption,
            "risk_level": risk_level,
            "obstacles_avoided": obstacles_avoided
        }
    
    def _assess_path_risk(self, path: List[Tuple[int, int]]) -> str:
        """
        评估路径风险
        
        Args:
            path: 路径点列表
            
        Returns:
            风险等级
        """
        risk_score = 0.0
        
        for point in path:
            # 检查是否靠近障碍物
            if self._is_near_obstacle(point):
                risk_score += 0.1
            
            # 检查是否靠近禁飞区
            if self._is_near_no_fly_zone(point):
                risk_score += 0.15
        
        # 根据风险分数确定等级
        if risk_score > 0.7:
            return "high"
        elif risk_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _is_near_obstacle(self, point: Tuple[int, int], threshold: int = 5) -> bool:
        """
        检查是否靠近障碍物
        
        Args:
            point: 检查点
            threshold: 阈值
            
        Returns:
            是否靠近障碍物
        """
        x, y = point
        
        for obstacle in self.obstacles:
            obs_x, obs_y = obstacle["position"]
            distance = math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2)
            if distance <= threshold:
                return True
        
        return False
    
    def _is_near_no_fly_zone(self, point: Tuple[int, int], threshold: int = 5) -> bool:
        """
        检查是否靠近禁飞区
        
        Args:
            point: 检查点
            threshold: 阈值
            
        Returns:
            是否靠近禁飞区
        """
        x, y = point
        
        for zone in self.no_fly_zones:
            center_x, center_y = zone["center"]
            radius = zone["radius"]
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= radius + threshold:
                return True
        
        return False
    
    def _extract_waypoints(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        提取路径点
        
        Args:
            path: 完整路径
            
        Returns:
            关键路径点列表
        """
        if len(path) <= 2:
            return path
        
        # 简化：每隔10个点取一个关键点
        waypoints = [path[0]]
        
        for i in range(10, len(path) - 1, 10):
            waypoints.append(path[i])
        
        waypoints.append(path[-1])
        
        return waypoints
    
    def _generate_altitude_profile(self, path: List[Tuple[int, int]]) -> List[int]:
        """
        生成高度轮廓
        
        Args:
            path: 路径点列表
            
        Returns:
            高度列表
        """
        altitude_profile = []
        
        for i, point in enumerate(path):
            # 基于地形生成高度
            base_altitude = 50  # 基础高度
            
            # 根据位置调整高度
            x, y = point
            altitude_adjustment = int(math.sin(x * 0.1) * 10 + math.cos(y * 0.1) * 5)
            
            altitude = base_altitude + altitude_adjustment
            altitude_profile.append(altitude)
        
        return altitude_profile
    
    def _generate_global_plan(self, route_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成全局路径规划
        
        Args:
            route_plans: 各无人机路径规划
            
        Returns:
            全局规划
        """
        # 收集所有路径点
        all_points = []
        for route in route_plans:
            all_points.extend(route.get("path", []))
        
        # 计算全局指标
        if not all_points:
            return {"total_coverage": 0, "conflict_points": []}
        
        # 计算覆盖范围
        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]
        
        coverage = {
            "min_x": min(x_coords),
            "max_x": max(x_coords),
            "min_y": min(y_coords),
            "max_y": max(y_coords),
            "area": (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
        }
        
        # 检测冲突点
        conflict_points = self._detect_conflict_points(route_plans)
        
        return {
            "coverage": coverage,
            "conflict_points": conflict_points,
            "coordination_required": len(conflict_points) > 0
        }
    
    def _detect_conflict_points(self, route_plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测冲突点
        
        Args:
            route_plans: 各无人机路径规划
            
        Returns:
            冲突点列表
        """
        conflict_points = []
        
        # 简化实现：检查路径交叉
        for i in range(len(route_plans)):
            for j in range(i + 1, len(route_plans)):
                route_i = route_plans[i].get("path", [])
                route_j = route_plans[j].get("path", [])
                
                # 检查路径点是否接近
                for point_i in route_i[:10]:  # 只检查前10个点
                    for point_j in route_j[:10]:
                        distance = math.sqrt((point_i[0] - point_j[0]) ** 2 + 
                                           (point_i[1] - point_j[1]) ** 2)
                        if distance < 5:  # 距离小于5认为冲突
                            conflict_points.append({
                                "point": point_i,
                                "drones": [route_plans[i]["drone_id"], route_plans[j]["drone_id"]],
                                "distance": distance
                            })
        
        return conflict_points
    
    def _calculate_overall_metrics(self, route_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算总体指标
        
        Args:
            route_plans: 各无人机路径规划
            
        Returns:
            总体指标
        """
        if not route_plans:
            return {}
        
        total_distance = sum(route.get("path_length", 0) for route in route_plans)
        total_time = max(route.get("estimated_time", 0) for route in route_plans)
        total_energy = sum(route.get("energy_consumption", 0) for route in route_plans)
        
        risk_levels = [route.get("risk_level", "low") for route in route_plans]
        avg_risk = sum(1 if r == "high" else 0.5 if r == "medium" else 0 for r in risk_levels) / len(risk_levels)
        
        return {
            "total_distance": total_distance,
            "total_time": total_time,
            "total_energy": total_energy,
            "average_risk_score": avg_risk,
            "path_efficiency": total_distance / len(route_plans) if route_plans else 0
        }
    
    def _generate_coordination_plan(self, route_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成协调计划
        
        Args:
            route_plans: 各无人机路径规划
            
        Returns:
            协调计划
        """
        # 生成通信协议
        communication_protocol = {
            "frequency": "5.8GHz",
            "encryption": "AES-256",
            "backup_channel": "satellite"
        }
        
        # 生成时间表
        time_slots = []
        for i, route in enumerate(route_plans):
            time_slots.append({
                "drone_id": route["drone_id"],
                "start_time": i * 2,  # 错开2分钟
                "end_time": i * 2 + route.get("estimated_time", 0)
            })
        
        return {
            "communication_protocol": communication_protocol,
            "time_slots": time_slots,
            "emergency_procedures": ["立即返回基地", "切换备用通道", "请求地面支援"]
        }
    
    def _generate_risk_mitigation_plan(self, route_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成风险缓解计划
        
        Args:
            route_plans: 各无人机路径规划
            
        Returns:
            风险缓解计划
        """
        risk_assessments = []
        
        for route in route_plans:
            risk_level = route.get("risk_level", "low")
            
            if risk_level == "high":
                mitigation = {
                    "drone_id": route["drone_id"],
                    "risk_level": risk_level,
                    "mitigation_actions": [
                        "降低飞行高度",
                        "增加侦察频率",
                        "准备紧急着陆"
                    ],
                    "contingency_plan": "切换到备用路径"
                }
            elif risk_level == "medium":
                mitigation = {
                    "drone_id": route["drone_id"],
                    "risk_level": risk_level,
                    "mitigation_actions": [
                        "保持安全距离",
                        "监控障碍物",
                        "准备规避动作"
                    ],
                    "contingency_plan": "调整飞行速度"
                }
            else:
                mitigation = {
                    "drone_id": route["drone_id"],
                    "risk_level": risk_level,
                    "mitigation_actions": ["常规监控"],
                    "contingency_plan": "无需特殊处理"
                }
            
            risk_assessments.append(mitigation)
        
        return {
            "risk_assessments": risk_assessments,
            "emergency_contacts": ["地面控制中心", "紧急救援队", "医疗团队"],
            "weather_contingency": "恶劣天气时暂停任务"
        }