"""
LangGraph 节点实现

包含爬虫节点、Agent 节点和集成节点
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .state import SEOState
from ..services.crawler import CrawlerService
from ..agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class CrawlerNode:
    """网站爬虫节点"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.crawler = CrawlerService(config)
    
    async def __call__(self, state: SEOState) -> SEOState:
        """执行爬虫任务"""
        logger.info(f"Starting crawler for {state.target_url}")
        
        try:
            state.crawl_status = "running"
            
            # 执行爬虫
            crawl_result = await self.crawler.crawl_url(state.target_url)
            
            # 转换为字典格式
            crawl_data = {
                "url": crawl_result.url,
                "status_code": crawl_result.status_code,
                "title": crawl_result.title,
                "meta_description": crawl_result.meta_description,
                "meta_keywords": crawl_result.meta_keywords,
                "headings": crawl_result.headings,
                "images": crawl_result.images,
                "links": crawl_result.links,
                "schema_org": crawl_result.schema_org,
                "load_time": crawl_result.load_time,
                "content_length": crawl_result.content_length,
                "lighthouse_scores": crawl_result.lighthouse_scores,
                "crawled_at": crawl_result.crawled_at.isoformat(),
                "error": crawl_result.error
            }
            
            state.crawl_data = crawl_data
            state.crawl_status = "completed"
            state.update_progress(20.0)  # 爬虫完成占 20% 进度
            
            logger.info(f"Crawler completed for {state.target_url}")
            
        except Exception as e:
            logger.error(f"Crawler failed for {state.target_url}: {str(e)}")
            state.crawl_status = "failed"
            state.error = f"Crawler error: {str(e)}"
        
        return state


class AgentNode:
    """通用 Agent 节点"""
    
    def __init__(self, agent: BaseAgent, result_field: str):
        self.agent = agent
        self.result_field = result_field
    
    async def __call__(self, state: SEOState) -> SEOState:
        """执行 Agent 分析"""
        logger.info(f"Starting {self.agent.name} agent")
        
        try:
            # 验证输入
            if not self.agent.validate_input(state):
                raise ValueError(f"Invalid input for {self.agent.name}")
            
            # 执行分析
            result = await self.agent.analyze(state)
            
            # 记录执行日志
            self.agent.log_execution(result)
            
            # 保存结果
            if result.success:
                setattr(state, self.result_field, result.data)
                
                # 更新进度（每个 Agent 占 15% 进度）
                current_progress = state.progress + 15.0
                state.update_progress(current_progress)
            else:
                state.error = f"{self.agent.name} failed: {result.error}"
                
        except Exception as e:
            logger.error(f"Agent {self.agent.name} failed: {str(e)}")
            state.error = f"{self.agent.name} error: {str(e)}"
        
        return state


class IntegratorNode:
    """结果集成节点"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    async def __call__(self, state: SEOState) -> SEOState:
        """集成所有 Agent 结果并生成优化计划"""
        logger.info("Starting result integration")
        
        try:
            # 收集所有洞察
            insights = {
                "keyword": state.keyword_insights,
                "content": state.content_insights,
                "technical": state.technical_insights,
                "geo": state.geo_insights,
                "link": state.link_insights,
                "serp": state.serp_insights,
                "local_seo": state.local_seo_insights,
                "gmb": state.gmb_insights,
                "geo_content": state.geo_content_insights,
                "competitor": state.competitor_insights
            }
            
            # 生成优化计划
            optimization_plan = await self._generate_optimization_plan(insights)
            
            state.optimization_plan = optimization_plan
            state.update_progress(100.0, "completed")
            
            logger.info("Result integration completed")
            
        except Exception as e:
            logger.error(f"Integration failed: {str(e)}")
            state.error = f"Integration error: {str(e)}"
            state.mark_failed(str(e))
        
        return state
    
    async def _generate_optimization_plan(self, insights: Dict[str, Any]) -> list:
        """生成优化计划"""
        plan = []
        
        # 基于各种洞察生成行动项
        if insights.get("content"):
            content_data = insights["content"]
            if not content_data.get("meta_description"):
                plan.append({
                    "action": "添加 Meta Description",
                    "category": "content",
                    "impact": 4,
                    "effort": 2,
                    "priority": "high",
                    "description": "页面缺少 Meta Description，建议添加 150-160 字符的描述"
                })

        if insights.get("technical"):
            technical_data = insights["technical"]
            # 检查页面性能
            page_performance = technical_data.get("page_performance", {})
            if page_performance.get("load_time", 0) > 3.0:
                plan.append({
                    "action": "优化页面加载速度",
                    "category": "technical",
                    "impact": 5,
                    "effort": 4,
                    "priority": "high",
                    "description": f"页面加载时间 {page_performance.get('load_time'):.1f}s，建议优化到 3s 以内"
                })

            # 检查技术SEO问题
            critical_issues = technical_data.get("critical_issues", [])
            for issue in critical_issues[:3]:  # 只处理前3个关键问题
                plan.append({
                    "action": issue.get("title", "修复技术问题"),
                    "category": "technical",
                    "impact": 5 if issue.get("severity") == "critical" else 4,
                    "effort": 3,
                    "priority": "high" if issue.get("severity") == "critical" else "medium",
                    "description": issue.get("description", "")
                })

        if insights.get("keyword"):
            keyword_data = insights["keyword"]
            # 处理关键词缺口
            keyword_gaps = keyword_data.get("keyword_gaps", [])
            if keyword_gaps:
                plan.append({
                    "action": "填补关键词缺口",
                    "category": "keyword",
                    "impact": 4,
                    "effort": 3,
                    "priority": "medium",
                    "description": f"发现 {len(keyword_gaps)} 个关键词缺口，建议增加相关内容"
                })

            # 处理关键词密度问题
            keyword_density = keyword_data.get("keyword_density", {})
            density_analysis = keyword_density.get("density_analysis", {})
            if density_analysis.get("over_optimized", 0) > 0:
                plan.append({
                    "action": "优化关键词密度",
                    "category": "keyword",
                    "impact": 3,
                    "effort": 2,
                    "priority": "medium",
                    "description": "部分关键词密度过高，需要调整避免过度优化"
                })

        if insights.get("geo"):
            geo_data = insights["geo"]
            # 处理NAP一致性问题
            nap_analysis = geo_data.get("nap_analysis", {})
            if nap_analysis.get("consistency_score", 100) < 90:
                plan.append({
                    "action": "改善NAP信息一致性",
                    "category": "geo",
                    "impact": 4,
                    "effort": 3,
                    "priority": "high",
                    "description": "公司名称、地址或电话信息存在不一致，影响本地SEO"
                })

        if insights.get("serp"):
            serp_data = insights["serp"]
            # 处理本地搜索机会
            local_opportunities = serp_data.get("local_search_opportunities", [])
            if local_opportunities:
                plan.append({
                    "action": "抓住本地搜索机会",
                    "category": "geo",
                    "impact": 4,
                    "effort": 3,
                    "priority": "medium",
                    "description": f"发现 {len(local_opportunities)} 个本地搜索优化机会"
                })

        # 处理本地SEO洞察
        if insights.get("local_seo"):
            local_seo_data = insights["local_seo"]
            local_seo_score = local_seo_data.get("local_seo_score", 0)
            if local_seo_score < 70:
                plan.append({
                    "action": "提升本地SEO表现",
                    "category": "local_seo",
                    "impact": 5,
                    "effort": 4,
                    "priority": "high",
                    "description": f"本地SEO分数仅{local_seo_score}分，需要全面优化"
                })

            # 处理本地SEO建议
            recommendations = local_seo_data.get("recommendations", [])
            for rec in recommendations[:2]:  # 只处理前2个建议
                plan.append({
                    "action": rec.get("title", "本地SEO优化"),
                    "category": "local_seo",
                    "impact": rec.get("impact", 3),
                    "effort": rec.get("effort", 3),
                    "priority": rec.get("priority", "medium"),
                    "description": rec.get("description", "")
                })

        # 处理GMB洞察
        if insights.get("gmb"):
            gmb_data = insights["gmb"]
            gmb_score = gmb_data.get("gmb_optimization_score", 0)
            if gmb_score < 80:
                plan.append({
                    "action": "优化Google My Business档案",
                    "category": "gmb",
                    "impact": 4,
                    "effort": 3,
                    "priority": "high",
                    "description": f"GMB优化分数{gmb_score}分，需要完善档案信息"
                })

        # 处理地理内容洞察
        if insights.get("geo_content"):
            geo_content_data = insights["geo_content"]
            content_score = geo_content_data.get("geo_content_score", 0)
            if content_score < 60:
                plan.append({
                    "action": "增强地理内容相关性",
                    "category": "geo_content",
                    "impact": 3,
                    "effort": 4,
                    "priority": "medium",
                    "description": f"地理内容分数{content_score}分，需要增加本地化内容"
                })

        # 处理内容洞察
        if insights.get("content"):
            content_data = insights["content"]
            content_score = content_data.get("content_quality_score", 0)
            if content_score < 70:
                plan.append({
                    "action": "提升内容质量",
                    "category": "content",
                    "impact": 4,
                    "effort": 3,
                    "priority": "high",
                    "description": f"内容质量分数{content_score}分，需要优化可读性、结构和深度"
                })

            # 处理内容缺口
            content_gaps = content_data.get("content_gaps", [])
            for gap in content_gaps[:2]:  # 只处理前2个缺口
                plan.append({
                    "action": gap.get("description", "填补内容缺口"),
                    "category": "content",
                    "impact": 3,
                    "effort": 2,
                    "priority": gap.get("priority", "medium"),
                    "description": gap.get("recommendation", "")
                })

        # 处理链接洞察
        if insights.get("link"):
            link_data = insights["link"]
            link_score = link_data.get("link_optimization_score", 0)
            if link_score < 60:
                plan.append({
                    "action": "优化链接建设策略",
                    "category": "link",
                    "impact": 4,
                    "effort": 4,
                    "priority": "medium",
                    "description": f"链接优化分数{link_score}分，需要改善内外链结构"
                })

            # 处理链接建设机会
            link_opportunities = link_data.get("link_opportunities", [])
            high_priority_opportunities = [opp for opp in link_opportunities if opp.get("priority") == "high"]
            if high_priority_opportunities:
                plan.append({
                    "action": "抓住链接建设机会",
                    "category": "link",
                    "impact": 4,
                    "effort": 3,
                    "priority": "medium",
                    "description": f"发现{len(high_priority_opportunities)}个高优先级链接建设机会"
                })

        # 处理竞争对手洞察
        if insights.get("competitor"):
            competitor_data = insights["competitor"]
            competition_intensity = competitor_data.get("competition_intensity", {})
            intensity_score = competition_intensity.get("intensity_score", 50)

            if intensity_score >= 70:
                plan.append({
                    "action": "制定竞争差异化策略",
                    "category": "competitor",
                    "impact": 5,
                    "effort": 4,
                    "priority": "high",
                    "description": f"竞争强度{intensity_score}分较高，需要差异化定位"
                })

            # 处理竞争机会
            swot_analysis = competitor_data.get("swot_analysis", {})
            opportunities = swot_analysis.get("opportunities", [])
            if opportunities:
                plan.append({
                    "action": "利用竞争机会",
                    "category": "competitor",
                    "impact": 4,
                    "effort": 3,
                    "priority": "medium",
                    "description": f"发现{len(opportunities)}个竞争机会，建议制定针对性策略"
                })
        
        # 按优先级和影响力排序
        plan.sort(key=lambda x: (x["priority"] == "high", x["impact"]), reverse=True)
        
        return plan


# 创建节点实例的工厂函数
def create_crawler_node(config: Dict[str, Any] = None) -> CrawlerNode:
    """创建爬虫节点"""
    return CrawlerNode(config)


def create_agent_node(agent: BaseAgent, result_field: str) -> AgentNode:
    """创建 Agent 节点"""
    return AgentNode(agent, result_field)


def create_integrator_node(config: Dict[str, Any] = None) -> IntegratorNode:
    """创建集成节点"""
    return IntegratorNode(config)
