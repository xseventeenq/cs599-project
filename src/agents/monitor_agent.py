"""
执行监控 Agent

负责实时状态跟踪、异常处理、进度报告和任务执行监控。
"""

import logging
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from langchain_core.language_models import BaseChatModel
except Exception:  # LangChain is optional for the deterministic demo
    BaseChatModel = object


class MonitorAgent:
    """执行监控 Agent，负责任务执行监控和异常处理"""
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化监控 Agent
        
        Args:
            llm: 语言模型实例
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        self.monitoring_history = []
        self.alert_thresholds = {
            "battery_low": 0.2,
            "risk_high": 0.7,
            "communication_loss": 30,  # 秒
            "deviation_threshold": 10  # 米
        }
    
    def monitor(self, route_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        监控任务执行
        
        Args:
            route_plan: 路径规划方案
            
        Returns:
            监控结果
        """
        self.logger.info("开始执行监控")
        
        # 1. 初始化监控状态
        monitoring_state = self._initialize_monitoring_state(route_plan)
        
        # 2. 模拟任务执行监控
        execution_logs = self._simulate_execution_monitoring(monitoring_state)
        
        # 3. 异常检测
        anomalies = self._detect_anomalies(execution_logs)
        
        # 4. 生成处理建议
        recommendations = self._generate_recommendations(anomalies, monitoring_state)
        
        # 5. 生成最终报告
        final_report = self._generate_final_report(monitoring_state, execution_logs, anomalies, recommendations)
        
        monitoring_result = {
            "monitoring_state": monitoring_state,
            "execution_logs": execution_logs,
            "anomalies": anomalies,
            "recommendations": recommendations,
            "final_report": final_report,
            "status": "completed" if not anomalies else "completed_with_warnings"
        }
        
        self.monitoring_history.append(monitoring_result)
        self.logger.info(f"执行监控完成，检测到 {len(anomalies)} 个异常")
        
        return monitoring_result
    
    def _initialize_monitoring_state(self, route_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        初始化监控状态
        
        Args:
            route_plan: 路径规划方案
            
        Returns:
            监控状态
        """
        drone_routes = route_plan.get("drone_routes", [])
        
        drone_states = []
        for route in drone_routes:
            drone_state = {
                "drone_id": route.get("drone_id", "unknown"),
                "status": "ready",
                "current_position": route.get("start_point", (0, 0)),
                "target_position": route.get("end_point", (0, 0)),
                "battery_level": 1.0,
                "progress": 0.0,
                "current_waypoint": 0,
                "communication_status": "connected",
                "last_update": datetime.now().isoformat(),
                "estimated_completion": route.get("estimated_time", 0)
            }
            drone_states.append(drone_state)
        
        monitoring_state = {
            "mission_id": route_plan.get("mission_id", "unknown"),
            "start_time": datetime.now().isoformat(),
            "drone_states": drone_states,
            "overall_progress": 0.0,
            "mission_status": "in_progress",
            "alerts": []
        }
        
        return monitoring_state
    
    def _simulate_execution_monitoring(self, monitoring_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        模拟执行监控
        
        Args:
            monitoring_state: 监控状态
            
        Returns:
            执行日志列表
        """
        execution_logs = []
        drone_states = monitoring_state.get("drone_states", [])
        
        # 模拟5个时间步的监控
        for step in range(5):
            step_logs = []
            
            for drone_state in drone_states:
                # 更新无人机状态
                updated_state = self._update_drone_state(drone_state, step)
                
                # 生成日志
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "step": step,
                    "drone_id": drone_state["drone_id"],
                    "status": updated_state["status"],
                    "position": updated_state["current_position"],
                    "battery_level": updated_state["battery_level"],
                    "progress": updated_state["progress"],
                    "message": self._generate_status_message(updated_state)
                }
                
                step_logs.append(log_entry)
                
                # 更新原始状态
                drone_state.update(updated_state)
            
            execution_logs.extend(step_logs)
            
            # 更新总体进度
            overall_progress = sum(d["progress"] for d in drone_states) / len(drone_states) if drone_states else 0
            monitoring_state["overall_progress"] = overall_progress
            
            # 模拟时间间隔
            # time.sleep(0.1)  # 实际演示中可以取消注释
        
        # 设置任务完成状态
        monitoring_state["mission_status"] = "completed"
        monitoring_state["end_time"] = datetime.now().isoformat()
        
        return execution_logs
    
    def _update_drone_state(self, drone_state: Dict[str, Any], step: int) -> Dict[str, Any]:
        """
        更新无人机状态
        
        Args:
            drone_state: 当前无人机状态
            step: 时间步
            
        Returns:
            更新后的状态
        """
        # 计算进度
        progress = min((step + 1) / 5.0, 1.0)
        
        # 计算当前位置
        current_pos = drone_state.get("current_position", (0, 0))
        target_pos = drone_state.get("target_position", (0, 0))
        
        # 线性插值计算位置
        start_pos = current_pos if step == 0 else drone_state.get("start_position", current_pos)
        if "start_position" not in drone_state:
            drone_state["start_position"] = current_pos
        
        start_pos = drone_state["start_position"]
        new_x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
        new_y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
        
        # 更新电池电量
        battery_consumption = 0.15 * progress  # 每步消耗15%
        new_battery = max(0.0, 1.0 - battery_consumption)
        
        # 随机生成一些状态变化
        status = "flying" if progress < 1.0 else "completed"
        communication_status = "connected"
        
        # 模拟偶发通信问题
        if random.random() < 0.05:
            communication_status = "unstable"
        
        return {
            "status": status,
            "current_position": (round(new_x, 2), round(new_y, 2)),
            "battery_level": round(new_battery, 2),
            "progress": round(progress, 2),
            "communication_status": communication_status,
            "last_update": datetime.now().isoformat()
        }
    
    def _generate_status_message(self, drone_state: Dict[str, Any]) -> str:
        """
        生成状态消息
        
        Args:
            drone_state: 无人机状态
            
        Returns:
            状态消息
        """
        status = drone_state.get("status", "unknown")
        progress = drone_state.get("progress", 0)
        battery = drone_state.get("battery_level", 0)
        
        if status == "completed":
            return f"任务完成，电池剩余 {battery:.0%}"
        elif status == "flying":
            return f"正在执行任务，进度 {progress:.0%}，电池剩余 {battery:.0%}"
        elif status == "ready":
            return "准备就绪，等待起飞"
        else:
            return f"状态: {status}"
    
    def _detect_anomalies(self, execution_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测异常
        
        Args:
            execution_logs: 执行日志
            
        Returns:
            异常列表
        """
        anomalies = []
        
        for log in execution_logs:
            # 检测低电量
            if log.get("battery_level", 1.0) < self.alert_thresholds["battery_low"]:
                anomalies.append({
                    "type": "battery_low",
                    "severity": "high",
                    "drone_id": log["drone_id"],
                    "timestamp": log["timestamp"],
                    "message": f"无人机 {log['drone_id']} 电量过低: {log['battery_level']:.0%}",
                    "recommended_action": "立即返航或切换备用无人机"
                })
            
            # 检测通信异常
            if log.get("communication_status") == "unstable":
                anomalies.append({
                    "type": "communication_unstable",
                    "severity": "medium",
                    "drone_id": log["drone_id"],
                    "timestamp": log["timestamp"],
                    "message": f"无人机 {log['drone_id']} 通信不稳定",
                    "recommended_action": "切换备用通信通道"
                })
            
            # 检测进度异常
            if log.get("progress", 0) < 0.2 and log.get("step", 0) > 2:
                anomalies.append({
                    "type": "progress_slow",
                    "severity": "medium",
                    "drone_id": log["drone_id"],
                    "timestamp": log["timestamp"],
                    "message": f"无人机 {log['drone_id']} 进度缓慢",
                    "recommended_action": "检查路径规划或调整任务分配"
                })
        
        return anomalies
    
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]], monitoring_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成处理建议
        
        Args:
            anomalies: 异常列表
            monitoring_state: 监控状态
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 按异常类型分组
        anomaly_types = {}
        for anomaly in anomalies:
            anomaly_type = anomaly["type"]
            if anomaly_type not in anomaly_types:
                anomaly_types[anomaly_type] = []
            anomaly_types[anomaly_type].append(anomaly)
        
        # 为每种异常类型生成建议
        for anomaly_type, anomaly_list in anomaly_types.items():
            if anomaly_type == "battery_low":
                recommendations.append({
                    "priority": "high",
                    "action": "电池管理",
                    "description": "立即调度低电量无人机返航，并启用备用无人机接替任务",
                    "affected_drones": [a["drone_id"] for a in anomaly_list],
                    "estimated_impact": "可能延迟任务完成5-10分钟"
                })
            elif anomaly_type == "communication_unstable":
                recommendations.append({
                    "priority": "medium",
                    "action": "通信恢复",
                    "description": "切换到备用通信通道，增加通信频率",
                    "affected_drones": [a["drone_id"] for a in anomaly_list],
                    "estimated_impact": "对任务影响较小"
                })
            elif anomaly_type == "progress_slow":
                recommendations.append({
                    "priority": "medium",
                    "action": "任务调整",
                    "description": "重新评估路径规划，必要时调整任务分配",
                    "affected_drones": [a["drone_id"] for a in anomaly_list],
                    "estimated_impact": "可能需要重新规划路径"
                })
        
        # 如果没有异常，生成常规建议
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "action": "常规监控",
                "description": "任务执行正常，继续保持监控",
                "affected_drones": [],
                "estimated_impact": "无"
            })
        
        return recommendations
    
    def _generate_final_report(self, monitoring_state: Dict[str, Any], execution_logs: List[Dict[str, Any]], 
                              anomalies: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成最终报告
        
        Args:
            monitoring_state: 监控状态
            execution_logs: 执行日志
            anomalies: 异常列表
            recommendations: 建议列表
            
        Returns:
            最终报告
        """
        # 统计执行结果
        drone_states = monitoring_state.get("drone_states", [])
        completed_drones = sum(1 for d in drone_states if d.get("status") == "completed")
        total_drones = len(drone_states)
        
        success_rate = completed_drones / total_drones if total_drones > 0 else 0
        
        # 计算平均电量
        avg_battery = sum(d.get("battery_level", 0) for d in drone_states) / total_drones if total_drones > 0 else 0
        
        # 计算任务持续时间
        start_time = monitoring_state.get("start_time")
        end_time = monitoring_state.get("end_time")
        duration = "未知"
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                duration = str(end_dt - start_dt)
            except:
                duration = "计算失败"
        
        # 异常统计
        anomaly_stats = {}
        for anomaly in anomalies:
            anomaly_type = anomaly["type"]
            anomaly_stats[anomaly_type] = anomaly_stats.get(anomaly_type, 0) + 1
        
        report = {
            "mission_id": monitoring_state.get("mission_id", "unknown"),
            "execution_summary": {
                "total_drones": total_drones,
                "completed_drones": completed_drones,
                "success_rate": success_rate,
                "overall_progress": monitoring_state.get("overall_progress", 0),
                "average_battery_remaining": avg_battery,
                "duration": duration
            },
            "anomaly_summary": {
                "total_anomalies": len(anomalies),
                "anomaly_types": anomaly_stats,
                "critical_anomalies": sum(1 for a in anomalies if a.get("severity") == "high")
            },
            "recommendations_summary": {
                "total_recommendations": len(recommendations),
                "high_priority": sum(1 for r in recommendations if r.get("priority") == "high"),
                "medium_priority": sum(1 for r in recommendations if r.get("priority") == "medium"),
                "low_priority": sum(1 for r in recommendations if r.get("priority") == "low")
            },
            "mission_status": "success" if success_rate >= 0.8 and len(anomalies) == 0 else "partial_success",
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def get_monitoring_history(self) -> List[Dict[str, Any]]:
        """
        获取监控历史
        
        Returns:
            监控历史列表
        """
        return self.monitoring_history.copy()
    
    def clear_history(self):
        """清空监控历史"""
        self.monitoring_history.clear()
        self.logger.info("监控历史已清空")