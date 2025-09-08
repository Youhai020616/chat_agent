"""
LangGraph 工作流定义

创建完整的 SEO & GEO 分析工作流
"""

import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import SEOState
from .nodes import CrawlerNode, AgentNode, IntegratorNode
from ..agents.geo import EntityAgent, SERPSpyAgent
from ..agents.seo import TechnicalAuditAgent, KeywordGapAgent

logger = logging.getLogger(__name__)


def create_seo_workflow(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """创建 SEO & GEO 分析工作流"""

    # 创建状态图
    workflow = StateGraph(SEOState)

    # 创建节点
    crawler_node = CrawlerNode(config)
    entity_agent = EntityAgent(config)
    serp_spy_agent = SERPSpyAgent(config)
    technical_audit_agent = TechnicalAuditAgent(config)
    keyword_gap_agent = KeywordGapAgent(config)
    integrator_node = IntegratorNode(config)

    # 添加节点到工作流
    workflow.add_node("crawler", crawler_node)
    workflow.add_node("entity_analysis", AgentNode(entity_agent, "geo_insights"))
    workflow.add_node("serp_analysis", AgentNode(serp_spy_agent, "serp_insights"))
    workflow.add_node("technical_audit", AgentNode(technical_audit_agent, "technical_insights"))
    workflow.add_node("keyword_gap", AgentNode(keyword_gap_agent, "keyword_insights"))
    workflow.add_node("integrator", integrator_node)

    # 定义工作流边
    workflow.set_entry_point("crawler")

    # 爬虫完成后并行执行所有分析
    workflow.add_edge("crawler", "entity_analysis")
    workflow.add_edge("crawler", "serp_analysis")
    workflow.add_edge("crawler", "technical_audit")
    workflow.add_edge("crawler", "keyword_gap")

    # 所有分析完成后进行集成
    workflow.add_edge("entity_analysis", "integrator")
    workflow.add_edge("serp_analysis", "integrator")
    workflow.add_edge("technical_audit", "integrator")
    workflow.add_edge("keyword_gap", "integrator")

    # 集成完成后结束
    workflow.add_edge("integrator", END)

    # 添加检查点保存器
    memory = MemorySaver()

    # 编译工作流
    app = workflow.compile(checkpointer=memory)

    return app


def create_full_seo_workflow(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """创建完整的 SEO 工作流（包含所有 Agent）"""
    
    # 这个函数将在后续里程碑中实现更多 Agent
    # 目前先返回基础的 GEO 工作流
    return create_seo_workflow(config)


async def execute_seo_analysis(
    target_url: str,
    locale: str = "zh-CN",
    site_id: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> SEOState:
    """执行 SEO 分析"""
    
    try:
        # 创建工作流
        workflow = create_seo_workflow(config)
        
        # 创建初始状态
        initial_state = SEOState(
            target_url=target_url,
            locale=locale,
            site_id=site_id
        )
        initial_state.mark_started()
        
        # 执行工作流
        thread_config = {"configurable": {"thread_id": f"analysis_{initial_state.run_id}"}}
        
        final_state = None
        async for state in workflow.astream(initial_state, config=thread_config):
            final_state = state
            logger.info(f"Workflow step completed: {state.progress}%")
        
        if final_state:
            final_state.mark_completed()
            return final_state
        else:
            raise Exception("Workflow execution failed")
            
    except Exception as e:
        logger.error(f"SEO analysis execution failed: {str(e)}")
        if 'initial_state' in locals():
            initial_state.mark_failed(str(e))
            return initial_state
        raise


def should_continue_to_integrator(state: SEOState) -> str:
    """决定是否继续到集成节点"""
    
    # 检查必要的分析是否完成
    required_analyses = ["geo_insights", "serp_insights"]
    completed_analyses = []
    
    if state.geo_insights:
        completed_analyses.append("geo_insights")
    if hasattr(state, 'serp_insights') and state.serp_insights:
        completed_analyses.append("serp_insights")
    
    # 如果所有必要分析都完成，继续到集成节点
    if all(analysis in completed_analyses for analysis in required_analyses):
        return "integrator"
    else:
        return "wait"  # 等待其他分析完成


def create_conditional_workflow(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """创建带条件路由的工作流"""
    
    workflow = StateGraph(SEOState)
    
    # 创建节点
    crawler_node = CrawlerNode(config)
    entity_agent = EntityAgent(config)
    serp_spy_agent = SERPSpyAgent(config)
    integrator_node = IntegratorNode(config)
    
    # 添加节点
    workflow.add_node("crawler", crawler_node)
    workflow.add_node("entity_analysis", AgentNode(entity_agent, "geo_insights"))
    workflow.add_node("serp_analysis", AgentNode(serp_spy_agent, "serp_insights"))
    workflow.add_node("integrator", integrator_node)
    workflow.add_node("wait", lambda state: state)  # 等待节点
    
    # 设置入口点
    workflow.set_entry_point("crawler")
    
    # 爬虫后的条件路由
    def after_crawler(state: SEOState) -> list:
        if state.crawl_status == "completed":
            return ["entity_analysis", "serp_analysis"]
        else:
            return [END]
    
    workflow.add_conditional_edges(
        "crawler",
        after_crawler
    )
    
    # 分析完成后的条件路由
    def after_analysis(state: SEOState) -> str:
        return should_continue_to_integrator(state)
    
    workflow.add_conditional_edges(
        "entity_analysis",
        after_analysis,
        {
            "integrator": "integrator",
            "wait": "wait"
        }
    )
    
    workflow.add_conditional_edges(
        "serp_analysis", 
        after_analysis,
        {
            "integrator": "integrator",
            "wait": "wait"
        }
    )
    
    # 等待节点的路由
    workflow.add_conditional_edges(
        "wait",
        after_analysis,
        {
            "integrator": "integrator",
            "wait": "wait"
        }
    )
    
    # 集成完成后结束
    workflow.add_edge("integrator", END)
    
    # 编译工作流
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
