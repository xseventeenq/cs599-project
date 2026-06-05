"""
向量记忆模块

用于保存历史任务经验，并支持基于关键词的经验检索。
当前版本采用轻量级 JSON 存储，后续可替换为 FAISS / Chroma。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class VectorMemory:
    """轻量级任务经验记忆库"""

    def __init__(self, storage_path: str = "./data/memory/experiences.json"):
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_data([])

    def save_experience(self, experience: Dict[str, Any]) -> str:
        """
        保存一次任务经验。

        Args:
            experience: 包含 mission、plan、metrics 的经验字典

        Returns:
            经验 ID
        """
        data = self._read_data()
        experience_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        record = {
            "id": experience_id,
            "created_at": datetime.now().isoformat(),
            "mission_type": experience.get("mission", {}).get("type", "unknown"),
            "location": experience.get("mission", {}).get("location", "unknown"),
            "summary": self._build_summary(experience),
            "experience": experience,
        }

        data.append(record)
        self._write_data(data)
        self.logger.info(f"保存任务经验: {experience_id}")
        return experience_id

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        检索历史经验。

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            匹配经验列表
        """
        data = self._read_data()
        query_tokens = set(query.lower().split())

        scored_records = []
        for record in data:
            text = json.dumps(record, ensure_ascii=False).lower()
            score = sum(1 for token in query_tokens if token in text)
            if score > 0 or query in text:
                scored_records.append((score, record))

        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [record for _, record in scored_records[:top_k]]

    def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出最近任务经验。"""
        data = self._read_data()
        return data[-limit:][::-1]

    def clear(self) -> None:
        """清空记忆库。"""
        self._write_data([])
        self.logger.info("任务经验记忆库已清空")

    def _build_summary(self, experience: Dict[str, Any]) -> str:
        mission = experience.get("mission", {})
        metrics = experience.get("metrics", {})
        return (
            f"任务类型: {mission.get('type', 'unknown')}; "
            f"地点: {mission.get('location', 'unknown')}; "
            f"成功率: {metrics.get('success_rate', 0):.2f}; "
            f"总代价: {metrics.get('total_cost', 0):.2f}; "
            f"平均风险: {metrics.get('average_risk', 0):.2f}"
        )

    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
