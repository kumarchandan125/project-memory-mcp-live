from fastmcp import FastMCP

from project_memory_mcp_live.tools.decision_tools import register_decision_tools
from project_memory_mcp_live.tools.project_tools import register_project_tools
from project_memory_mcp_live.tools.task_tools import register_task_tools
from project_memory_mcp_live.tools.update_tools import register_update_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register every application tool with the MCP server."""

    register_project_tools(mcp)
    register_task_tools(mcp)
    register_update_tools(mcp)
    register_decision_tools(mcp)