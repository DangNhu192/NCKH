# modules/agency/agency_router.py
"""
Agency Agents Roster API Router for WEB SUPER v2.0
Exposes agent personalities, missions, rules, and deliverables to frontend.
"""

from fastapi import APIRouter, HTTPException
from modules.shared.agency_agents_registry import get_all_agents, get_agent_by_id

agency_router = APIRouter(tags=["The Agency - AI Specialists Roster"])

@agency_router.get("/api/agency/agents")
def list_agency_agents():
    """Trả về danh sách Hội đồng 10 Giáo sư Nghiêm khắc trong hệ sinh thái Agency Agents WEB SUPER"""
    agents = get_all_agents()
    return {
        "success": True,
        "total_agents": len(agents),
        "pattern": "msitarzewski/agency-agents",
        "council": "Council of 10 Rigorous Academic Professors",
        "agents": agents
    }

@agency_router.get("/api/agency/agents/{agent_id}")
def get_agency_agent_details(agent_id: str):
    agent = get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chuyên gia AI: {agent_id}")
    return {
        "success": True,
        "agent": agent.to_dict()
    }
