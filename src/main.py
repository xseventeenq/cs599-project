"""
UAV-Mission-Agent 主入口模块

提供多智能体协作的无人机任务分配系统。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from src.config import get_config
from src.agents.task_analyzer import TaskAnalyzerAgent
from src.agents.fleet_manager import FleetManagerAgent
from src.agents.route_planner import RoutePlannerAgent
from src.agents.monitor_agent import MonitorAgent
from src.memory.vector_memory import VectorMemory


class UAVMissionAgent:
    """多智能体协作的无人机任务分配系统"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化任务分配系统
        
        Args:
            env_file: 环境变量文件路径
        """
        # 加载配置
        self.config = get_config()
        
        # 初始化日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个 Agent
        self.task_analyzer = TaskAnalyzerAgent()
        self.fleet_manager = FleetManagerAgent()
        self.route_planner = RoutePlannerAgent()
        self.monitor_agent = MonitorAgent()
        
        # 初始化记忆系统
        self.memory = VectorMemory()
        
        self.logger.info("UAV-Mission-Agent 初始化完成")
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get_logging_config()
        Path(log_config["file"]).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def execute(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务分配
        
        Args:
            mission: 任务描述字典，包含类型、位置、优先级等
            
        Returns:
            包含调度方案和评估指标的结果字典
        """
        self.logger.info(f"开始执行任务: {mission.get('type', 'unknown')}")
        
        try:
            # 1. 任务分析
            self.logger.info("步骤1: 任务分析")
            analyzed_mission = self.task_analyzer.analyze(mission)
            
            # 2. 资源调度
            self.logger.info("步骤2: 资源调度")
            drone_allocation = self.fleet_manager.allocate(analyzed_mission)
            
            # 3. 路径规划
            self.logger.info("步骤3: 路径规划")
            route_plan = self.route_planner.plan(drone_allocation)
            
            # 4. 执行监控
            self.logger.info("步骤4: 执行监控")
            monitoring_result = self.monitor_agent.monitor(route_plan)
            
            # 5. 生成最终方案
            final_plan = {
                "mission": mission,
                "analyzed_mission": analyzed_mission,
                "drone_allocation": drone_allocation,
                "route_plan": route_plan,
                "monitoring": monitoring_result,
                "status": "completed"
            }
            
            # 6. 评估指标
            metrics = self._calculate_metrics(final_plan)
            
            # 7. 保存到记忆
            self.memory.save_experience({
                "mission": mission,
                "plan": final_plan,
                "metrics": metrics
            })
            
            result = {
                "plan": final_plan,
                "metrics": metrics,
                "status": "success"
            }
            
            self.logger.info(f"任务分配完成，成功率: {metrics.get('success_rate', 0):.2%}")
            return result
            
        except Exception as e:
            self.logger.error(f"任务执行失败: {str(e)}")
            return {
                "plan": None,
                "metrics": None,
                "status": "failed",
                "error": str(e)
            }
    
    def _calculate_metrics(self, plan: Dict[str, Any]) -> Dict[str, float]:
        """
        计算评估指标
        
        Args:
            plan: 最终调度方案
            
        Returns:
            评估指标字典
        """
        # 这里简化计算，实际应基于plan内容计算
        metrics = {
            "success_rate": 0.0,
            "total_cost": 0.0,
            "average_risk": 0.0,
            "collaboration_efficiency": 0.0
        }
        
        # 基于任务类型和约束计算简单指标
        mission = plan.get("mission", {})
        mission_type = mission.get("type", "unknown")
        
        if mission_type == "disaster_rescue":
            metrics["success_rate"] = 0.85
            metrics["total_cost"] = 1000.0
            metrics["average_risk"] = 0.3
        elif mission_type == "delivery":
            metrics["success_rate"] = 0.95
            metrics["total_cost"] = 500.0
            metrics["average_risk"] = 0.1
        else:
            metrics["success_rate"] = 0.8
            metrics["total_cost"] = 800.0
            metrics["average_risk"] = 0.2
        
        return metrics
    
    def save_plan(self, result: Dict[str, Any], output_path: str = "./data/output"):
        """
        保存调度方案
        
        Args:
            result: 执行结果
            output_path: 输出目录
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mission_plan_{timestamp}.json"
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"调度方案已保存到: {filepath}")
        return filepath


def main():
    """主函数"""
    # 创建 Agent 实例
    agent = UAVMissionAgent()
    
    # 示例任务
    sample_mission = {
        "type": "disaster_rescue",
        "location": "城市A区域",
        "priority": "high",
        "objects": ["受困人员", "医疗物资"],
        "constraints": ["恶劣天气", "复杂地形"],
        "num_drones": 3,
        "max_distance": 50.0,
        "time_limit": 60
    }
    
    print("=== UAV-Mission-Agent 多智能体协作系统 ===")
    print(f"任务类型: {sample_mission['type']}")
    print(f"任务位置: {sample_mission['location']}")
    print()
    
    # 执行任务分配
    result = agent.execute(sample_mission)
    
    # 输出结果
    if result["status"] == "success":
        print("✅ 任务分配成功！")
        print(f"成功率: {result['metrics']['success_rate']:.2%}")
        print(f"总代价: {result['metrics']['total_cost']:.2f}")
        print(f"平均风险: {result['metrics']['average_risk']:.2f}")
        
        # 保存结果
        output_path = agent.save_plan(result)
        print(f"详细方案已保存到: {output_path}")
    else:
        print("❌ 任务分配失败！")
        print(f"错误信息: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()