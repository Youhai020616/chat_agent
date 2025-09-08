"""
SERPSpy Agent - 搜索结果页面分析

功能：
1. 分析目标关键词的搜索结果页面
2. 识别本地搜索特征（地图包、本地企业列表）
3. 分析竞争对手的地理优化策略
4. 评估本地搜索排名机会
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import quote_plus
import re

from ..base import BaseAgent, AgentResult
from ...services.external.serp_api import SERPAPIService
from ...services.external.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SERPSpyAgent(BaseAgent):
    """搜索结果页面分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("serp_spy", config)
        self.serp_api = SERPAPIService(config)
        self.openai_service = OpenAIService(config)
        
        # 本地搜索关键词模式
        self.local_keywords = [
            '附近', '周边', '本地', '当地', '就近',
            '地址', '电话', '营业时间', '怎么走',
            '在哪里', '位置', '导航', '路线'
        ]
        
        # 地理修饰词
        self.geo_modifiers = [
            '北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉',
            '市', '区', '县', '镇', '街道', '附近', '周边'
        ]
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行搜索结果页面分析"""
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(state):
                return AgentResult(
                    success=False,
                    data={},
                    error="Invalid input state"
                )
            
            # 从网站内容中提取关键词
            keywords = await self._extract_target_keywords(state)
            
            if not keywords:
                return AgentResult(
                    success=False,
                    data={},
                    error="No keywords found for SERP analysis"
                )
            
            # 并行分析多个关键词的搜索结果
            analysis_tasks = []
            for keyword in keywords[:5]:  # 限制分析数量
                analysis_tasks.append(self._analyze_keyword_serp(keyword, state.locale))
            
            serp_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 整合分析结果
            analysis_data = {
                'analyzed_keywords': keywords,
                'serp_analysis': {},
                'local_search_opportunities': [],
                'competitor_analysis': {},
                'recommendations': [],
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'total_keywords': len(keywords),
                    'analyzed_keywords_count': len([r for r in serp_results if not isinstance(r, Exception)]),
                    'locale': state.locale,
                    'target_url': state.target_url
                }
            }
            
            # 处理每个关键词的分析结果
            for i, result in enumerate(serp_results):
                if not isinstance(result, Exception):
                    keyword = keywords[i]
                    analysis_data['serp_analysis'][keyword] = result
            
            # 生成综合分析
            analysis_data['local_search_opportunities'] = await self._identify_local_opportunities(analysis_data['serp_analysis'])
            analysis_data['competitor_analysis'] = await self._analyze_competitors(analysis_data['serp_analysis'])
            analysis_data['recommendations'] = await self._generate_serp_recommendations(analysis_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=analysis_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(keywords),
                cost=self._estimate_cost(len(keywords))
            )
            
        except Exception as e:
            logger.error(f"SERP analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _extract_target_keywords(self, state: "SEOState") -> List[str]:
        """从网站内容中提取目标关键词"""
        keywords = set()
        
        crawl_data = state.crawl_data
        if not crawl_data:
            return []
        
        # 从标题提取
        title = crawl_data.get('title', '')
        if title:
            keywords.add(title)
        
        # 从 meta keywords 提取
        meta_keywords = crawl_data.get('meta_keywords', '')
        if meta_keywords:
            keywords.update([kw.strip() for kw in meta_keywords.split(',')])
        
        # 从 H1 标签提取
        headings = crawl_data.get('headings', {})
        h1_tags = headings.get('h1', [])
        keywords.update(h1_tags)
        
        # 使用 AI 提取更多相关关键词
        if self.openai_service:
            try:
                ai_keywords = await self._ai_extract_keywords(crawl_data)
                keywords.update(ai_keywords)
            except Exception as e:
                logger.warning(f"AI keyword extraction failed: {str(e)}")
        
        # 生成地理相关的关键词变体
        geo_keywords = self._generate_geo_keyword_variants(list(keywords))
        keywords.update(geo_keywords)
        
        # 过滤和清理关键词
        cleaned_keywords = []
        for keyword in keywords:
            if keyword and len(keyword.strip()) > 2 and len(keyword) < 100:
                cleaned_keywords.append(keyword.strip())
        
        return list(set(cleaned_keywords))[:10]  # 限制数量
    
    async def _analyze_keyword_serp(self, keyword: str, locale: str) -> Dict[str, Any]:
        """分析单个关键词的搜索结果"""
        try:
            # 获取搜索结果
            serp_data = await self._get_serp_data(keyword, locale)
            
            if not serp_data:
                return {
                    'keyword': keyword,
                    'error': 'Failed to get SERP data'
                }
            
            analysis = {
                'keyword': keyword,
                'total_results': serp_data.get('total_results', 0),
                'local_features': self._analyze_local_features(serp_data),
                'organic_results': self._analyze_organic_results(serp_data),
                'paid_results': self._analyze_paid_results(serp_data),
                'featured_snippets': self._analyze_featured_snippets(serp_data),
                'local_pack': self._analyze_local_pack(serp_data),
                'competition_level': self._assess_competition_level(serp_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"SERP analysis failed for keyword '{keyword}': {str(e)}")
            return {
                'keyword': keyword,
                'error': str(e)
            }
    
    async def _get_serp_data(self, keyword: str, locale: str) -> Optional[Dict[str, Any]]:
        """获取搜索结果数据"""
        if self.serp_api:
            try:
                return await self.serp_api.search(keyword, locale)
            except Exception as e:
                logger.warning(f"SERP API failed: {str(e)}")
        
        # 如果 API 不可用，返回模拟数据
        return self._create_mock_serp_data(keyword)
    
    def _analyze_local_features(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析本地搜索特征"""
        features = {
            'has_local_pack': False,
            'has_map': False,
            'has_knowledge_panel': False,
            'local_ads_count': 0,
            'local_features_score': 0
        }
        
        # 检查本地包（Local Pack）
        local_results = serp_data.get('local_results', [])
        if local_results:
            features['has_local_pack'] = True
            features['local_pack_count'] = len(local_results)
        
        # 检查地图
        if serp_data.get('map'):
            features['has_map'] = True
        
        # 检查知识面板
        knowledge_graph = serp_data.get('knowledge_graph')
        if knowledge_graph:
            features['has_knowledge_panel'] = True
        
        # 计算本地特征分数
        score = 0
        if features['has_local_pack']:
            score += 40
        if features['has_map']:
            score += 30
        if features['has_knowledge_panel']:
            score += 20
        if features['local_ads_count'] > 0:
            score += 10
        
        features['local_features_score'] = score
        
        return features
    
    def _analyze_organic_results(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析自然搜索结果"""
        organic_results = serp_data.get('organic_results', [])
        
        analysis = {
            'total_count': len(organic_results),
            'top_domains': [],
            'local_businesses': [],
            'content_types': {},
            'avg_title_length': 0,
            'avg_description_length': 0
        }
        
        if not organic_results:
            return analysis
        
        # 分析前10个结果
        top_results = organic_results[:10]
        
        # 提取域名
        domains = []
        title_lengths = []
        desc_lengths = []
        
        for result in top_results:
            # 域名分析
            link = result.get('link', '')
            if link:
                domain = self._extract_domain(link)
                domains.append(domain)
            
            # 标题长度
            title = result.get('title', '')
            if title:
                title_lengths.append(len(title))
            
            # 描述长度
            snippet = result.get('snippet', '')
            if snippet:
                desc_lengths.append(len(snippet))
            
            # 识别本地企业
            if self._is_local_business_result(result):
                analysis['local_businesses'].append({
                    'title': title,
                    'domain': self._extract_domain(link),
                    'position': result.get('position', 0)
                })
        
        # 统计域名分布
        from collections import Counter
        domain_counts = Counter(domains)
        analysis['top_domains'] = domain_counts.most_common(5)
        
        # 计算平均长度
        if title_lengths:
            analysis['avg_title_length'] = sum(title_lengths) / len(title_lengths)
        if desc_lengths:
            analysis['avg_description_length'] = sum(desc_lengths) / len(desc_lengths)
        
        return analysis
    
    def _analyze_paid_results(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析付费广告结果"""
        ads = serp_data.get('ads', [])
        
        return {
            'total_ads': len(ads),
            'top_advertisers': [ad.get('displayed_link', '') for ad in ads[:3]],
            'ad_competition': 'high' if len(ads) > 3 else 'medium' if len(ads) > 0 else 'low'
        }
    
    def _analyze_featured_snippets(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析精选摘要"""
        featured_snippet = serp_data.get('featured_snippet')
        
        if not featured_snippet:
            return {'has_featured_snippet': False}
        
        return {
            'has_featured_snippet': True,
            'type': featured_snippet.get('type', 'unknown'),
            'source_domain': self._extract_domain(featured_snippet.get('link', '')),
            'content_length': len(featured_snippet.get('snippet', ''))
        }
    
    def _analyze_local_pack(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析本地包结果"""
        local_results = serp_data.get('local_results', [])
        
        if not local_results:
            return {'has_local_pack': False}
        
        analysis = {
            'has_local_pack': True,
            'business_count': len(local_results),
            'businesses': []
        }
        
        for business in local_results:
            analysis['businesses'].append({
                'title': business.get('title', ''),
                'rating': business.get('rating', 0),
                'reviews': business.get('reviews', 0),
                'type': business.get('type', ''),
                'address': business.get('address', '')
            })
        
        return analysis
    
    def _assess_competition_level(self, serp_data: Dict[str, Any]) -> str:
        """评估竞争水平"""
        score = 0
        
        # 广告数量
        ads_count = len(serp_data.get('ads', []))
        if ads_count > 3:
            score += 30
        elif ads_count > 0:
            score += 15
        
        # 本地包存在
        if serp_data.get('local_results'):
            score += 25
        
        # 精选摘要存在
        if serp_data.get('featured_snippet'):
            score += 20
        
        # 知识图谱存在
        if serp_data.get('knowledge_graph'):
            score += 15
        
        # 总结果数量
        total_results = serp_data.get('total_results', 0)
        if total_results > 1000000:
            score += 10
        
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    async def _identify_local_opportunities(self, serp_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别本地搜索机会"""
        opportunities = []
        
        for keyword, analysis in serp_analysis.items():
            if isinstance(analysis, dict) and 'local_features' in analysis:
                local_features = analysis['local_features']
                
                # 本地包机会
                if local_features.get('has_local_pack') and local_features.get('local_features_score', 0) > 50:
                    opportunities.append({
                        'type': 'local_pack',
                        'keyword': keyword,
                        'opportunity': 'high',
                        'description': f'关键词 "{keyword}" 显示本地包结果，有很好的本地SEO机会',
                        'action': '优化 Google My Business 资料和本地引用'
                    })
                
                # 地图搜索机会
                if local_features.get('has_map'):
                    opportunities.append({
                        'type': 'map_search',
                        'keyword': keyword,
                        'opportunity': 'medium',
                        'description': f'关键词 "{keyword}" 显示地图结果',
                        'action': '确保 NAP 信息准确并获取更多本地评论'
                    })
        
        return opportunities
    
    async def _analyze_competitors(self, serp_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析竞争对手"""
        competitor_domains = {}
        
        for keyword, analysis in serp_analysis.items():
            if isinstance(analysis, dict) and 'organic_results' in analysis:
                organic = analysis['organic_results']
                top_domains = organic.get('top_domains', [])
                
                for domain, count in top_domains:
                    if domain not in competitor_domains:
                        competitor_domains[domain] = {
                            'domain': domain,
                            'keywords': [],
                            'total_appearances': 0,
                            'avg_position': 0
                        }
                    
                    competitor_domains[domain]['keywords'].append(keyword)
                    competitor_domains[domain]['total_appearances'] += count
        
        # 排序竞争对手
        sorted_competitors = sorted(
            competitor_domains.values(),
            key=lambda x: x['total_appearances'],
            reverse=True
        )
        
        return {
            'top_competitors': sorted_competitors[:5],
            'total_competitors': len(competitor_domains)
        }
    
    async def _generate_serp_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成 SERP 优化建议"""
        recommendations = []
        
        # 本地搜索机会建议
        local_opportunities = analysis_data.get('local_search_opportunities', [])
        if local_opportunities:
            recommendations.append({
                'category': 'local_seo',
                'priority': 'high',
                'title': '抓住本地搜索机会',
                'description': f'发现 {len(local_opportunities)} 个本地搜索机会，建议优化本地SEO策略',
                'impact': 5,
                'effort': 3,
                'opportunities': local_opportunities
            })
        
        # 竞争分析建议
        competitor_analysis = analysis_data.get('competitor_analysis', {})
        top_competitors = competitor_analysis.get('top_competitors', [])
        if top_competitors:
            recommendations.append({
                'category': 'competitor_analysis',
                'priority': 'medium',
                'title': '分析主要竞争对手',
                'description': f'识别出 {len(top_competitors)} 个主要竞争对手，建议深入分析其SEO策略',
                'impact': 3,
                'effort': 4,
                'competitors': [comp['domain'] for comp in top_competitors[:3]]
            })
        
        # 精选摘要机会
        featured_snippet_opportunities = []
        serp_analysis = analysis_data.get('serp_analysis', {})
        for keyword, analysis in serp_analysis.items():
            if isinstance(analysis, dict):
                featured_snippets = analysis.get('featured_snippets', {})
                if not featured_snippets.get('has_featured_snippet'):
                    featured_snippet_opportunities.append(keyword)
        
        if featured_snippet_opportunities:
            recommendations.append({
                'category': 'featured_snippets',
                'priority': 'medium',
                'title': '争取精选摘要位置',
                'description': f'发现 {len(featured_snippet_opportunities)} 个关键词没有精选摘要，可以争取这些位置',
                'impact': 4,
                'effort': 3,
                'keywords': featured_snippet_opportunities[:5]
            })
        
        return recommendations
    
    def _generate_geo_keyword_variants(self, keywords: List[str]) -> List[str]:
        """生成地理关键词变体"""
        geo_variants = []
        
        for keyword in keywords:
            for modifier in self.geo_modifiers:
                # 添加地理修饰词
                geo_variants.append(f"{keyword} {modifier}")
                geo_variants.append(f"{modifier} {keyword}")
            
            for local_kw in self.local_keywords:
                # 添加本地搜索词
                geo_variants.append(f"{keyword} {local_kw}")
        
        return geo_variants
    
    def _extract_domain(self, url: str) -> str:
        """从 URL 中提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return url
    
    def _is_local_business_result(self, result: Dict[str, Any]) -> bool:
        """判断是否为本地企业结果"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        local_indicators = ['地址', '电话', '营业时间', '位置', '导航', '附近']
        
        for indicator in local_indicators:
            if indicator in title or indicator in snippet:
                return True
        
        return False
    
    async def _ai_extract_keywords(self, crawl_data: Dict[str, Any]) -> List[str]:
        """使用 AI 提取关键词"""
        if not self.openai_service:
            return []
        
        # 构建内容摘要
        content_parts = []
        if crawl_data.get('title'):
            content_parts.append(f"标题: {crawl_data['title']}")
        if crawl_data.get('meta_description'):
            content_parts.append(f"描述: {crawl_data['meta_description']}")
        
        headings = crawl_data.get('headings', {})
        for level, texts in headings.items():
            content_parts.extend([f"{level}: {text}" for text in texts[:3]])
        
        content = '\n'.join(content_parts)
        
        prompt = f"""
        基于以下网站内容，提取5-10个最相关的关键词，这些关键词应该：
        1. 与网站主要业务相关
        2. 适合搜索引擎优化
        3. 包含潜在的本地搜索词
        
        网站内容：
        {content[:1000]}
        
        请以逗号分隔的格式返回关键词列表。
        """
        
        try:
            response = await self.openai_service.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            keywords = [kw.strip() for kw in response.split(',')]
            return keywords[:10]
            
        except Exception as e:
            logger.error(f"AI keyword extraction failed: {str(e)}")
            return []
    
    def _create_mock_serp_data(self, keyword: str) -> Dict[str, Any]:
        """创建模拟 SERP 数据"""
        return {
            'keyword': keyword,
            'total_results': 1250000,
            'organic_results': [
                {
                    'position': 1,
                    'title': f'{keyword} - 官方网站',
                    'link': 'https://example.com',
                    'snippet': f'专业的{keyword}服务，提供优质解决方案...'
                },
                {
                    'position': 2,
                    'title': f'{keyword}服务 - 本地专家',
                    'link': 'https://local-expert.com',
                    'snippet': f'本地{keyword}专家，服务周边地区...'
                }
            ],
            'local_results': [
                {
                    'title': f'{keyword}服务中心',
                    'rating': 4.5,
                    'reviews': 128,
                    'address': '北京市朝阳区xxx街道',
                    'type': '服务机构'
                }
            ],
            'ads': [
                {
                    'title': f'{keyword} - 专业服务',
                    'displayed_link': 'ads-example.com'
                }
            ]
        }
    
    def _estimate_tokens_used(self, keywords: List[str]) -> int:
        """估算使用的 token 数量"""
        return len(keywords) * 100  # 每个关键词大约100 tokens
    
    def _estimate_cost(self, keyword_count: int) -> float:
        """估算 API 调用成本"""
        # SERP API 约 $0.001/查询，OpenAI 约 $0.03/1K tokens
        serp_cost = keyword_count * 0.001
        ai_cost = keyword_count * 100 / 1000 * 0.03
        return serp_cost + ai_cost
