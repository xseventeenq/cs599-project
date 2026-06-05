import json
import streamlit as st

from src.main import UAVMissionAgent

st.set_page_config(page_title="UAV-Mission-Agent", layout="wide")
st.title("UAV-Mission-Agent：多无人机任务分配 Agent 系统")

mission_text = st.text_area(
    "输入任务 JSON",
    value=json.dumps({
        "type": "disaster_rescue",
        "location": "城市A区域",
        "priority": "high",
        "objects": ["受困人员", "医疗物资"],
        "constraints": ["恶劣天气", "复杂地形"],
        "num_drones": 3,
        "time_limit": 60
    }, ensure_ascii=False, indent=2),
    height=260,
)

if st.button("执行任务分配"):
    mission = json.loads(mission_text)
    agent = UAVMissionAgent()
    result = agent.execute(mission)
    st.subheader("评估指标")
    st.json(result.get("metrics"))
    st.subheader("完整结果")
    st.json(result)
