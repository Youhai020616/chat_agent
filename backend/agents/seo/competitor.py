"""
Competitor Agent - 竞争对手深度分析

功能：
1. 竞争对手识别和分析
2. 关键词竞争分析
3. 内容策略对比
4. 技术SEO对比
5. 竞争优势和劣势分析
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter
from urllib.parse import urlparse

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService
from ...services.external.serp_api import SERPAPIService

logger = logging.getLogger(__name__)


class CompetitorAgent(BaseAgent):
    """竞争对手深度分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("competitor", config)
        self.openai_service = OpenAIService(config)
        self.serp_api = SERPAPIService(config)
        
        # 竞争分析维度
        self.analysis_dimensions = {
            'keyword_competition': {'weight': 0.25, 'max_score': 100},
            'content_strategy': {'weight': 0.20, 'max_score': 100},
            'technical_seo': {'weight': 0.20, 'max_score': 100},
            'link_profile': {'weight': 0.15, 'max_score': 100},
            'user_experience': {'weight': 0.10, 'max_score': 100},
            'brand_presence': {'weight': 0.10, 'max_score': 100}
        }
        
        # 竞争强度评估标准
        self.competition_levels = {
            'low': {'threshold': 30, 'description': '竞争较小，机会较多'},
            'medium': {'threshold': 60, 'description': '竞争适中，需要策略'},
            'high': {'threshold': 80, 'description': '竞争激烈，需要差异化'},
            'very_high': {'threshold': 100, 'description': '竞争极其激烈，需要创新'}
        }
        
        # 分析指标
        self.metrics = {
            'domain_authority': '域名权威度',
            'page_authority': '页面权威度',
            'backlink_count': '外链数量',
            'referring_domains': '引用域名数',
            'organic_keywords': '有机关键词数',
            'organic_traffic': '有机流量',
            'content_freshness': '内容新鲜度',
            'technical_score': '技术SEO分数'
        }
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行竞争对手深度分析"""
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(state):
                return AgentResult(
                    success=False,
                    data={},
                    error="Invalid input state"
                )
            
            # 获取之前的分析结果
            crawl_data = state.crawl_data
            keyword_insights = state.keyword_insights
            technical_insights = state.technical_insights
            serp_insights = state.serp_insights
            
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行竞争分析任务
            tasks = [
                self._identify_competitors(crawl_data, keyword_insights, state.locale),
                self._analyze_keyword_competition(keyword_insights, serp_insights),
                self._analyze_content_strategy(crawl_data, keyword_insights),
                self._analyze_technical_competition(technical_insights),
                self._analyze_competitive_landscape(state.target_url, state.locale)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            competitor_data = {
                'identified_competitors': results[0] if not isinstance(results[0], Exception) else [],
                'keyword_competition': results[1] if not isinstance(results[1], Exception) else {},
                'content_strategy_analysis': results[2] if not isinstance(results[2], Exception) else {},
                'technical_competition': results[3] if not isinstance(results[3], Exception) else {},
                'competitive_landscape': results[4] if not isinstance(results[4], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算竞争强度分数
            competitor_data['competition_intensity'] = await self._calculate_competition_intensity(competitor_data)
            
            # 生成竞争策略建议
            competitor_data['competitive_strategy'] = await self._generate_competitive_strategy(competitor_data, keyword_insights)
            
            # 识别竞争优势和劣势
            competitor_data['swot_analysis'] = await self._perform_swot_analysis(competitor_data, crawl_data)
            
            # 生成竞争优化建议
            competitor_data['recommendations'] = await self._generate_competitive_recommendations(competitor_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=competitor_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(competitor_data),
                cost=self._estimate_cost(competitor_data)
            )
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _identify_competitors(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]], locale: str) -> List[Dict[str, Any]]:
        """识别竞争对手"""
        competitors = []
        
        # 基于关键词识别竞争对手
        if keyword_insights and self.serp_api and self.serp_api.is_available():
            try:
                current_keywords = keyword_insights.get('current_keywords', [])
                primary_keywords = [kw['keyword'] for kw in current_keywords[:5]]
                
                for keyword in primary_keywords:
                    # 搜索关键词获取竞争对手
                    search_results = await self.serp_api.search(keyword, locale)
                    
                    if search_results and 'organic_results' in search_results:
                        for result in search_results['organic_results'][:5]:
                            domain = urlparse(result.get('link', '')).netloc
                            if domain:
                                competitor = {
                                    'domain': domain,
                                    'title': result.get('title', ''),
                                    'url': result.get('link', ''),
                                    'position': result.get('position', 0),
                                    'keyword': keyword,
                                    'snippet': result.get('snippet', '')
                                }
                                competitors.append(competitor)
                    
                    # 添加延迟避免API限制
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Competitor identification failed: {str(e)}")
        
        # 去重并排序
        unique_competitors = {}
        for comp in competitors:
            domain = comp['domain']
            if domain not in unique_competitors:
                unique_competitors[domain] = {
                    'domain': domain,
                    'appearances': 1,
                    'keywords': [comp['keyword']],
                    'avg_position': comp['position'],
                    'sample_title': comp['title'],
                    'sample_url': comp['url']
                }
            else:
                unique_competitors[domain]['appearances'] += 1
                unique_competitors[domain]['keywords'].append(comp['keyword'])
                unique_competitors[domain]['avg_position'] = (
                    unique_competitors[domain]['avg_position'] + comp['position']
                ) / 2
        
        # 按出现频次排序
        sorted_competitors = sorted(
            unique_competitors.values(),
            key=lambda x: x['appearances'],
            reverse=True
        )
        
        return sorted_competitors[:10]  # 返回前10个竞争对手
    
    async def _analyze_keyword_competition(self, keyword_insights: Optional[Dict[str, Any]], serp_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析关键词竞争"""
        keyword_competition = {
            'competitive_keywords': [],
            'keyword_difficulty': {},
            'opportunity_keywords': [],
            'competition_score': 0
        }
        
        if not keyword_insights:
            return keyword_competition
        
        current_keywords = keyword_insights.get('current_keywords', [])
        
        # 分析关键词竞争难度
        for kw_data in current_keywords[:10]:
            keyword = kw_data['keyword']
            frequency = kw_data.get('frequency', 0)
            
            # 简化的竞争难度评估
            difficulty_score = 50  # 基础难度
            
            # 基于关键词长度调整难度
            if len(keyword.split()) == 1:
                difficulty_score += 30  # 单词关键词竞争更激烈
            elif len(keyword.split()) >= 3:
                difficulty_score -= 20  # 长尾关键词竞争较小
            
            # 基于频率调整难度
            if frequency >= 5:
                difficulty_score += 20
            elif frequency <= 2:
                difficulty_score -= 10
            
            difficulty_level = 'low'
            if difficulty_score >= 80:
                difficulty_level = 'very_high'
            elif difficulty_score >= 60:
                difficulty_level = 'high'
            elif difficulty_score >= 40:
                difficulty_level = 'medium'
            
            keyword_competition['competitive_keywords'].append({
                'keyword': keyword,
                'difficulty_score': min(100, max(0, difficulty_score)),
                'difficulty_level': difficulty_level,
                'frequency': frequency
            })
        
        # 识别机会关键词
        keyword_gaps = keyword_insights.get('keyword_gaps', [])
        for gap in keyword_gaps[:5]:
            if gap.get('priority') in ['high', 'medium']:
                keyword_competition['opportunity_keywords'].append({
                    'keyword': gap['keyword'],
                    'opportunity_type': gap.get('gap_type', 'unknown'),
                    'priority': gap.get('priority', 'medium')
                })
        
        # 计算总体竞争分数
        if keyword_competition['competitive_keywords']:
            avg_difficulty = sum(
                kw['difficulty_score'] for kw in keyword_competition['competitive_keywords']
            ) / len(keyword_competition['competitive_keywords'])
            keyword_competition['competition_score'] = int(avg_difficulty)
        
        return keyword_competition
    
    async def _analyze_content_strategy(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析内容策略竞争"""
        content_analysis = {
            'content_gaps': [],
            'content_opportunities': [],
            'content_quality_comparison': {},
            'content_strategy_score': 0
        }
        
        # 分析当前内容质量
        title = crawl_data.get('title', '')
        meta_desc = crawl_data.get('meta_description', '')
        headings = crawl_data.get('headings', {})
        
        content_quality = {
            'title_optimization': bool(title and 30 <= len(title) <= 60),
            'meta_description_optimization': bool(meta_desc and 120 <= len(meta_desc) <= 160),
            'heading_structure': len(headings.get('h1', [])) == 1,
            'content_depth': sum(len(texts) for texts in headings.values()) >= 5
        }
        
        content_analysis['content_quality_comparison'] = content_quality
        
        # 识别内容缺口
        if not content_quality['title_optimization']:
            content_analysis['content_gaps'].append({
                'type': 'title_optimization',
                'description': '标题长度不符合SEO最佳实践',
                'priority': 'high'
            })
        
        if not content_quality['meta_description_optimization']:
            content_analysis['content_gaps'].append({
                'type': 'meta_description',
                'description': '缺少或Meta描述长度不当',
                'priority': 'high'
            })
        
        # 基于关键词识别内容机会
        if keyword_insights:
            keyword_opportunities = keyword_insights.get('keyword_opportunities', [])
            for opp in keyword_opportunities[:3]:
                content_analysis['content_opportunities'].append({
                    'keyword': opp['keyword'],
                    'opportunity_score': opp.get('opportunity_score', 0),
                    'content_type': 'informational',  # 简化处理
                    'priority': 'medium'
                })
        
        # 计算内容策略分数
        quality_score = sum(1 for v in content_quality.values() if v) / len(content_quality) * 100
        content_analysis['content_strategy_score'] = int(quality_score)
        
        return content_analysis
    
    async def _analyze_technical_competition(self, technical_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析技术SEO竞争"""
        technical_competition = {
            'technical_score': 0,
            'technical_advantages': [],
            'technical_weaknesses': [],
            'improvement_areas': []
        }
        
        if not technical_insights:
            return technical_competition
        
        # 获取技术SEO分数
        overall_score = technical_insights.get('overall_score', 0)
        technical_competition['technical_score'] = overall_score
        
        # 分析技术优势和劣势
        page_performance = technical_insights.get('page_performance', {})
        load_time = page_performance.get('load_time', 0)
        
        if load_time <= 2.0:
            technical_competition['technical_advantages'].append({
                'area': 'page_speed',
                'description': f'页面加载速度{load_time:.1f}s优秀',
                'competitive_advantage': 'high'
            })
        elif load_time > 3.0:
            technical_competition['technical_weaknesses'].append({
                'area': 'page_speed',
                'description': f'页面加载速度{load_time:.1f}s较慢',
                'improvement_priority': 'high'
            })
        
        # 分析Meta标签优化
        meta_tags = technical_insights.get('meta_tags', {})
        meta_score = meta_tags.get('meta_score', 0)
        
        if meta_score >= 90:
            technical_competition['technical_advantages'].append({
                'area': 'meta_optimization',
                'description': f'Meta标签优化分数{meta_score}分优秀',
                'competitive_advantage': 'medium'
            })
        elif meta_score < 70:
            technical_competition['technical_weaknesses'].append({
                'area': 'meta_optimization',
                'description': f'Meta标签优化分数{meta_score}分需要改进',
                'improvement_priority': 'medium'
            })
        
        # 识别改进领域
        critical_issues = technical_insights.get('critical_issues', [])
        for issue in critical_issues[:3]:
            technical_competition['improvement_areas'].append({
                'area': issue.get('type', 'unknown'),
                'description': issue.get('description', ''),
                'priority': issue.get('severity', 'medium')
            })
        
        return technical_competition
    
    async def _analyze_competitive_landscape(self, target_url: str, locale: str) -> Dict[str, Any]:
        """分析竞争环境"""
        landscape = {
            'market_saturation': 'medium',
            'entry_barriers': 'medium',
            'competitive_intensity': 'medium',
            'market_opportunities': [],
            'threats': []
        }
        
        # 简化的市场分析
        domain = urlparse(target_url).netloc
        
        # 基于域名特征评估市场
        if any(keyword in domain.lower() for keyword in ['seo', 'marketing', 'digital']):
            landscape['market_saturation'] = 'high'
            landscape['competitive_intensity'] = 'high'
            landscape['entry_barriers'] = 'high'
            
            landscape['threats'] = [
                '市场竞争激烈，新进入者众多',
                '技术门槛相对较低，容易被模仿',
                '客户获取成本较高'
            ]
            
            landscape['market_opportunities'] = [
                '专业化细分市场机会',
                '技术创新差异化',
                '本地化服务优势'
            ]
        else:
            landscape['market_opportunities'] = [
                '市场空间相对较大',
                '竞争对手较少',
                '品牌建设机会'
            ]
        
        return landscape
    
    async def _calculate_competition_intensity(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算竞争强度"""
        intensity_analysis = {
            'overall_intensity': 'medium',
            'intensity_score': 50,
            'key_factors': [],
            'intensity_breakdown': {}
        }
        
        # 基于竞争对手数量
        competitors_count = len(competitor_data.get('identified_competitors', []))
        competitor_factor = min(100, competitors_count * 10)
        
        # 基于关键词竞争
        keyword_competition = competitor_data.get('keyword_competition', {})
        keyword_factor = keyword_competition.get('competition_score', 50)
        
        # 基于技术竞争
        technical_competition = competitor_data.get('technical_competition', {})
        technical_factor = 100 - technical_competition.get('technical_score', 50)
        
        # 计算综合强度分数
        intensity_score = (competitor_factor * 0.4 + keyword_factor * 0.4 + technical_factor * 0.2)
        intensity_analysis['intensity_score'] = int(intensity_score)
        
        # 确定强度级别
        if intensity_score >= 80:
            intensity_analysis['overall_intensity'] = 'very_high'
        elif intensity_score >= 60:
            intensity_analysis['overall_intensity'] = 'high'
        elif intensity_score >= 40:
            intensity_analysis['overall_intensity'] = 'medium'
        else:
            intensity_analysis['overall_intensity'] = 'low'
        
        intensity_analysis['intensity_breakdown'] = {
            'competitor_density': competitor_factor,
            'keyword_difficulty': keyword_factor,
            'technical_barriers': technical_factor
        }
        
        return intensity_analysis
    
    async def _generate_competitive_strategy(self, competitor_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成竞争策略"""
        strategy = {
            'strategic_focus': [],
            'differentiation_opportunities': [],
            'competitive_tactics': [],
            'resource_allocation': {}
        }
        
        # 基于竞争强度确定策略重点
        competition_intensity = competitor_data.get('competition_intensity', {})
        intensity_level = competition_intensity.get('overall_intensity', 'medium')
        
        if intensity_level == 'very_high':
            strategy['strategic_focus'] = [
                '差异化定位',
                '细分市场专业化',
                '技术创新',
                '品牌建设'
            ]
            strategy['competitive_tactics'] = [
                '避开正面竞争',
                '寻找蓝海市场',
                '建立技术壁垒',
                '强化客户关系'
            ]
        elif intensity_level == 'high':
            strategy['strategic_focus'] = [
                '产品差异化',
                '服务优化',
                '成本控制',
                '市场细分'
            ]
            strategy['competitive_tactics'] = [
                '快速响应市场变化',
                '提升服务质量',
                '优化运营效率',
                '加强品牌推广'
            ]
        else:
            strategy['strategic_focus'] = [
                '市场扩张',
                '品牌建设',
                '产品完善',
                '客户获取'
            ]
            strategy['competitive_tactics'] = [
                '积极市场推广',
                '扩大市场份额',
                '建立行业地位',
                '优化用户体验'
            ]
        
        # 识别差异化机会
        content_analysis = competitor_data.get('content_strategy_analysis', {})
        content_gaps = content_analysis.get('content_gaps', [])
        
        for gap in content_gaps:
            strategy['differentiation_opportunities'].append({
                'opportunity': gap['type'],
                'description': gap['description'],
                'potential_impact': 'medium'
            })
        
        return strategy
    
    async def _perform_swot_analysis(self, competitor_data: Dict[str, Any], crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行SWOT分析"""
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # 分析优势
        technical_competition = competitor_data.get('technical_competition', {})
        technical_advantages = technical_competition.get('technical_advantages', [])
        
        for advantage in technical_advantages:
            swot['strengths'].append({
                'area': advantage['area'],
                'description': advantage['description'],
                'impact': advantage.get('competitive_advantage', 'medium')
            })
        
        # 分析劣势
        technical_weaknesses = technical_competition.get('technical_weaknesses', [])
        for weakness in technical_weaknesses:
            swot['weaknesses'].append({
                'area': weakness['area'],
                'description': weakness['description'],
                'priority': weakness.get('improvement_priority', 'medium')
            })
        
        # 分析机会
        keyword_competition = competitor_data.get('keyword_competition', {})
        opportunity_keywords = keyword_competition.get('opportunity_keywords', [])
        
        for opp in opportunity_keywords:
            swot['opportunities'].append({
                'type': 'keyword_opportunity',
                'description': f'关键词"{opp["keyword"]}"存在优化机会',
                'priority': opp.get('priority', 'medium')
            })
        
        # 分析威胁
        competitive_landscape = competitor_data.get('competitive_landscape', {})
        threats = competitive_landscape.get('threats', [])
        
        for threat in threats:
            swot['threats'].append({
                'type': 'market_threat',
                'description': threat,
                'severity': 'medium'
            })
        
        return swot
    
    async def _generate_competitive_recommendations(self, competitor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成竞争优化建议"""
        recommendations = []
        
        # 基于竞争强度生成建议
        competition_intensity = competitor_data.get('competition_intensity', {})
        intensity_score = competition_intensity.get('intensity_score', 50)
        
        if intensity_score >= 70:
            recommendations.append({
                'category': 'competitive_strategy',
                'priority': 'high',
                'title': '制定差异化竞争策略',
                'description': f'竞争强度{intensity_score}分较高，需要通过差异化避开正面竞争',
                'impact': 5,
                'effort': 4
            })
        
        # 基于关键词竞争生成建议
        keyword_competition = competitor_data.get('keyword_competition', {})
        opportunity_keywords = keyword_competition.get('opportunity_keywords', [])
        
        if opportunity_keywords:
            recommendations.append({
                'category': 'keyword_strategy',
                'priority': 'medium',
                'title': '抓住关键词机会',
                'description': f'发现{len(opportunity_keywords)}个关键词机会，建议优先优化',
                'impact': 4,
                'effort': 3
            })
        
        # 基于技术竞争生成建议
        technical_competition = competitor_data.get('technical_competition', {})
        improvement_areas = technical_competition.get('improvement_areas', [])
        
        for area in improvement_areas[:2]:  # 只处理前2个改进领域
            recommendations.append({
                'category': 'technical_improvement',
                'priority': area.get('priority', 'medium'),
                'title': f'改进{area.get("area", "技术")}',
                'description': area.get('description', ''),
                'impact': 3,
                'effort': 3
            })
        
        return recommendations
    
    def _estimate_tokens_used(self, competitor_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 竞争分析主要基于规则和API数据，AI使用适中
        base_tokens = 400
        competitors_count = len(competitor_data.get('identified_competitors', []))
        return base_tokens + competitors_count * 50
    
    def _estimate_cost(self, competitor_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(competitor_data)
        # OpenAI + SERP API 成本
        openai_cost = tokens / 1000 * 0.03
        serp_cost = 0.02  # SERP API 成本
        return openai_cost + serp_cost
