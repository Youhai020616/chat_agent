"""
LocalSEO Agent - 本地 SEO 优化分析

功能：
1. 本地搜索排名分析
2. Google My Business 优化检查
3. 本地引用（Citations）一致性分析
4. 本地关键词策略评估
5. 竞争对手本地SEO分析
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService
from ...services.external.google_places import GooglePlacesService
from ...services.external.serp_api import SERPAPIService

logger = logging.getLogger(__name__)


class LocalSEOAgent(BaseAgent):
    """本地 SEO 优化分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("local_seo", config)
        self.openai_service = OpenAIService(config)
        self.places_service = GooglePlacesService(config)
        self.serp_api = SERPAPIService(config)
        
        # 本地SEO评估标准
        self.local_seo_factors = {
            'gmb_completeness': {'weight': 0.25, 'max_score': 100},
            'nap_consistency': {'weight': 0.20, 'max_score': 100},
            'local_citations': {'weight': 0.15, 'max_score': 100},
            'local_keywords': {'weight': 0.15, 'max_score': 100},
            'reviews_ratings': {'weight': 0.15, 'max_score': 100},
            'local_content': {'weight': 0.10, 'max_score': 100}
        }
        
        # 本地关键词模式
        self.local_keyword_patterns = [
            r'附近的?(.+)',
            r'(.+)在(.+)',
            r'(.+)(.+市|.+区|.+县)',
            r'本地(.+)',
            r'当地(.+)',
            r'(.+)服务(.+地区|.+市|.+区)'
        ]
        
        # 重要的本地引用平台
        self.citation_platforms = [
            '百度地图', '高德地图', '腾讯地图',
            '大众点评', '美团', '58同城',
            '赶集网', '百度百科', '搜狗百科'
        ]
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行本地 SEO 分析"""
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
            geo_insights = state.geo_insights
            
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行本地SEO分析任务
            tasks = [
                self._analyze_gmb_optimization(crawl_data, geo_insights),
                self._analyze_local_keywords(crawl_data, state.locale),
                self._analyze_local_citations(geo_insights),
                self._analyze_local_competition(state.target_url, state.locale),
                self._analyze_local_content(crawl_data),
                self._analyze_reviews_strategy(geo_insights)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            local_seo_data = {
                'gmb_analysis': results[0] if not isinstance(results[0], Exception) else {},
                'local_keywords': results[1] if not isinstance(results[1], Exception) else {},
                'local_citations': results[2] if not isinstance(results[2], Exception) else {},
                'local_competition': results[3] if not isinstance(results[3], Exception) else {},
                'local_content': results[4] if not isinstance(results[4], Exception) else {},
                'reviews_strategy': results[5] if not isinstance(results[5], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算本地SEO总分
            local_seo_data['local_seo_score'] = await self._calculate_local_seo_score(local_seo_data)
            
            # 生成本地SEO优化建议
            local_seo_data['recommendations'] = await self._generate_local_seo_recommendations(local_seo_data)
            
            # 识别本地SEO机会
            local_seo_data['opportunities'] = await self._identify_local_opportunities(local_seo_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=local_seo_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(local_seo_data),
                cost=self._estimate_cost(local_seo_data)
            )
            
        except Exception as e:
            logger.error(f"Local SEO analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_gmb_optimization(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析 Google My Business 优化情况"""
        gmb_analysis = {
            'has_gmb_info': False,
            'completeness_score': 0,
            'optimization_issues': [],
            'missing_elements': [],
            'recommendations': []
        }
        
        # 检查是否有GMB相关信息
        schema_entities = geo_insights.get('schema_entities', {}) if geo_insights else {}
        organizations = schema_entities.get('organizations', [])
        
        gmb_info = {}
        for org in organizations:
            if org.get('name') and org.get('address'):
                gmb_info = org
                gmb_analysis['has_gmb_info'] = True
                break
        
        if gmb_analysis['has_gmb_info']:
            # 评估GMB信息完整性
            required_fields = ['name', 'address', 'telephone', 'url']
            optional_fields = ['description', 'openingHours', 'priceRange', 'image']
            
            completeness = 0
            for field in required_fields:
                if gmb_info.get(field):
                    completeness += 25  # 每个必需字段25分
                else:
                    gmb_analysis['missing_elements'].append({
                        'field': field,
                        'importance': 'high',
                        'description': f'缺少{field}信息'
                    })
            
            for field in optional_fields:
                if gmb_info.get(field):
                    completeness += 5  # 每个可选字段5分
                else:
                    gmb_analysis['missing_elements'].append({
                        'field': field,
                        'importance': 'medium',
                        'description': f'建议添加{field}信息'
                    })
            
            gmb_analysis['completeness_score'] = min(100, completeness)
            
            # 检查优化问题
            if gmb_info.get('name'):
                name = gmb_info['name']
                if len(name) > 50:
                    gmb_analysis['optimization_issues'].append({
                        'type': 'name_too_long',
                        'severity': 'medium',
                        'message': f'企业名称过长({len(name)}字符)，建议控制在50字符以内'
                    })
            
            if gmb_info.get('description'):
                desc = gmb_info['description']
                if len(desc) < 100:
                    gmb_analysis['optimization_issues'].append({
                        'type': 'description_too_short',
                        'severity': 'low',
                        'message': '企业描述过短，建议详细描述业务和服务'
                    })
        else:
            gmb_analysis['missing_elements'].append({
                'field': 'gmb_presence',
                'importance': 'critical',
                'description': '未发现Google My Business信息'
            })
        
        return gmb_analysis
    
    async def _analyze_local_keywords(self, crawl_data: Dict[str, Any], locale: str) -> Dict[str, Any]:
        """分析本地关键词策略"""
        local_keywords_analysis = {
            'current_local_keywords': [],
            'missing_local_keywords': [],
            'local_keyword_density': {},
            'geo_modifier_usage': {},
            'recommendations': []
        }
        
        # 提取所有文本内容
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        if not all_text:
            return local_keywords_analysis
        
        # 识别当前的本地关键词
        for pattern in self.local_keyword_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    keyword = ' '.join(match).strip()
                else:
                    keyword = match.strip()
                
                if keyword and len(keyword) > 2:
                    local_keywords_analysis['current_local_keywords'].append({
                        'keyword': keyword,
                        'pattern': pattern,
                        'context': 'content'
                    })
        
        # 分析地理修饰词使用情况
        geo_modifiers = ['附近', '本地', '当地', '周边', '就近', '市', '区', '县', '镇']
        for modifier in geo_modifiers:
            count = all_text.lower().count(modifier)
            if count > 0:
                local_keywords_analysis['geo_modifier_usage'][modifier] = count
        
        # 生成缺失的本地关键词建议
        if self.openai_service and self.openai_service.is_available():
            try:
                missing_keywords = await self._generate_local_keyword_suggestions(all_text)
                local_keywords_analysis['missing_local_keywords'] = missing_keywords
            except Exception as e:
                logger.warning(f"Local keyword generation failed: {str(e)}")
        
        return local_keywords_analysis
    
    async def _analyze_local_citations(self, geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析本地引用情况"""
        citations_analysis = {
            'found_citations': [],
            'citation_consistency': 0,
            'missing_platforms': [],
            'inconsistencies': [],
            'recommendations': []
        }
        
        if not geo_insights:
            return citations_analysis
        
        # 获取NAP信息
        nap_analysis = geo_insights.get('nap_analysis', {})
        business_entities = geo_insights.get('business_entities', {})
        
        # 模拟引用分析（实际实现需要爬取各大平台）
        citations_analysis['found_citations'] = [
            {
                'platform': '百度地图',
                'name': business_entities.get('company_names', [''])[0] if business_entities.get('company_names') else '',
                'address': nap_analysis.get('address_variations', [''])[0] if nap_analysis.get('address_variations') else '',
                'phone': nap_analysis.get('phone_variations', [''])[0] if nap_analysis.get('phone_variations') else '',
                'status': 'found'
            }
        ]
        
        # 计算引用一致性
        if nap_analysis.get('consistency_score'):
            citations_analysis['citation_consistency'] = nap_analysis['consistency_score']
        
        # 识别缺失的平台
        found_platforms = [citation['platform'] for citation in citations_analysis['found_citations']]
        citations_analysis['missing_platforms'] = [
            platform for platform in self.citation_platforms 
            if platform not in found_platforms
        ]
        
        return citations_analysis
    
    async def _analyze_local_competition(self, target_url: str, locale: str) -> Dict[str, Any]:
        """分析本地竞争环境"""
        competition_analysis = {
            'local_competitors': [],
            'market_saturation': 'unknown',
            'competitive_advantages': [],
            'competitive_gaps': [],
            'recommendations': []
        }
        
        if not self.places_service or not self.places_service.is_available():
            return competition_analysis
        
        try:
            # 基于网站内容推断业务类型和位置
            # 这里简化处理，实际应该从之前的分析中获取
            business_type = "SEO服务"  # 示例
            location = "北京"  # 示例
            
            # 分析本地竞争
            competition_data = await self.places_service.analyze_local_competition(business_type, location)
            
            if competition_data and 'analysis' in competition_data:
                analysis = competition_data['analysis']
                competition_analysis['market_saturation'] = analysis.get('market_saturation', 'unknown')
                
                # 处理竞争对手数据
                competitors = competition_data.get('competitors', [])[:5]
                for competitor in competitors:
                    competition_analysis['local_competitors'].append({
                        'name': competitor.get('name', ''),
                        'rating': competitor.get('rating', 0),
                        'reviews': competitor.get('user_ratings_total', 0),
                        'place_id': competitor.get('place_id', '')
                    })
                
                # 分析竞争优势和差距
                avg_rating = analysis.get('avg_rating', 0)
                if avg_rating > 0:
                    competition_analysis['competitive_gaps'].append({
                        'area': 'rating_improvement',
                        'description': f'平均竞争对手评分为{avg_rating:.1f}，需要提升服务质量和客户满意度'
                    })
        
        except Exception as e:
            logger.error(f"Local competition analysis failed: {str(e)}")
        
        return competition_analysis
    
    async def _analyze_local_content(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析本地内容优化"""
        content_analysis = {
            'local_content_score': 0,
            'local_signals': [],
            'missing_local_elements': [],
            'recommendations': []
        }
        
        # 检查本地信号
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        local_signals = [
            {'signal': '地址信息', 'pattern': r'地址|位置|坐落于', 'found': False, 'importance': 'high'},
            {'signal': '服务区域', 'pattern': r'服务|覆盖|业务范围', 'found': False, 'importance': 'medium'},
            {'signal': '联系方式', 'pattern': r'电话|手机|联系', 'found': False, 'importance': 'high'},
            {'signal': '营业时间', 'pattern': r'营业|开放|工作时间', 'found': False, 'importance': 'medium'},
            {'signal': '本地地标', 'pattern': r'附近|周边|临近', 'found': False, 'importance': 'low'}
        ]
        
        score = 0
        for signal in local_signals:
            if re.search(signal['pattern'], all_text, re.IGNORECASE):
                signal['found'] = True
                if signal['importance'] == 'high':
                    score += 30
                elif signal['importance'] == 'medium':
                    score += 20
                else:
                    score += 10
            else:
                content_analysis['missing_local_elements'].append({
                    'element': signal['signal'],
                    'importance': signal['importance'],
                    'recommendation': f'建议在内容中添加{signal["signal"]}'
                })
        
        content_analysis['local_content_score'] = min(100, score)
        content_analysis['local_signals'] = local_signals
        
        return content_analysis
    
    async def _analyze_reviews_strategy(self, geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析评论策略"""
        reviews_analysis = {
            'current_reviews': {},
            'review_strategy_score': 0,
            'review_opportunities': [],
            'recommendations': []
        }
        
        # 基于schema数据分析评论情况
        if geo_insights:
            schema_entities = geo_insights.get('schema_entities', {})
            organizations = schema_entities.get('organizations', [])
            
            for org in organizations:
                if org.get('name'):
                    # 模拟评论数据（实际需要从各平台获取）
                    reviews_analysis['current_reviews'][org['name']] = {
                        'total_reviews': 0,
                        'average_rating': 0,
                        'recent_reviews': 0,
                        'response_rate': 0
                    }
        
        # 评估评论策略
        if not reviews_analysis['current_reviews']:
            reviews_analysis['review_opportunities'].append({
                'opportunity': 'establish_review_presence',
                'priority': 'high',
                'description': '建立在线评论存在感，鼓励客户留下评论'
            })
        
        return reviews_analysis
    
    async def _calculate_local_seo_score(self, local_seo_data: Dict[str, Any]) -> int:
        """计算本地SEO总分"""
        total_score = 0
        
        for factor, config in self.local_seo_factors.items():
            factor_score = 0
            
            if factor == 'gmb_completeness':
                gmb_analysis = local_seo_data.get('gmb_analysis', {})
                factor_score = gmb_analysis.get('completeness_score', 0)
            
            elif factor == 'nap_consistency':
                # 从geo_insights获取NAP一致性分数
                factor_score = 85  # 示例分数
            
            elif factor == 'local_citations':
                citations = local_seo_data.get('local_citations', {})
                factor_score = citations.get('citation_consistency', 0)
            
            elif factor == 'local_keywords':
                keywords = local_seo_data.get('local_keywords', {})
                current_keywords = len(keywords.get('current_local_keywords', []))
                factor_score = min(100, current_keywords * 10)
            
            elif factor == 'reviews_ratings':
                reviews = local_seo_data.get('reviews_strategy', {})
                factor_score = reviews.get('review_strategy_score', 0)
            
            elif factor == 'local_content':
                content = local_seo_data.get('local_content', {})
                factor_score = content.get('local_content_score', 0)
            
            # 加权计算
            weighted_score = factor_score * config['weight']
            total_score += weighted_score
        
        return int(total_score)
    
    async def _generate_local_seo_recommendations(self, local_seo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成本地SEO优化建议"""
        recommendations = []
        
        # GMB优化建议
        gmb_analysis = local_seo_data.get('gmb_analysis', {})
        if not gmb_analysis.get('has_gmb_info'):
            recommendations.append({
                'category': 'gmb_setup',
                'priority': 'critical',
                'title': '创建Google My Business档案',
                'description': '建立GMB档案是本地SEO的基础，可以显著提升本地搜索可见性',
                'impact': 5,
                'effort': 3
            })
        elif gmb_analysis.get('completeness_score', 0) < 80:
            recommendations.append({
                'category': 'gmb_optimization',
                'priority': 'high',
                'title': '完善GMB信息',
                'description': f'GMB完整度仅{gmb_analysis.get("completeness_score", 0)}%，建议补充缺失信息',
                'impact': 4,
                'effort': 2
            })
        
        # 本地关键词建议
        local_keywords = local_seo_data.get('local_keywords', {})
        if len(local_keywords.get('current_local_keywords', [])) < 5:
            recommendations.append({
                'category': 'local_keywords',
                'priority': 'medium',
                'title': '增加本地关键词',
                'description': '当前本地关键词覆盖不足，建议在内容中增加地理位置相关关键词',
                'impact': 3,
                'effort': 2
            })
        
        # 本地引用建议
        citations = local_seo_data.get('local_citations', {})
        missing_platforms = citations.get('missing_platforms', [])
        if len(missing_platforms) > 5:
            recommendations.append({
                'category': 'local_citations',
                'priority': 'medium',
                'title': '建立本地引用',
                'description': f'在{len(missing_platforms)}个重要平台上缺少企业信息，建议建立本地引用',
                'impact': 3,
                'effort': 4
            })
        
        # 本地内容建议
        local_content = local_seo_data.get('local_content', {})
        if local_content.get('local_content_score', 0) < 60:
            recommendations.append({
                'category': 'local_content',
                'priority': 'medium',
                'title': '优化本地内容',
                'description': '增加本地化内容，包括地址、服务区域、本地地标等信息',
                'impact': 3,
                'effort': 3
            })
        
        return recommendations
    
    async def _identify_local_opportunities(self, local_seo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别本地SEO机会"""
        opportunities = []
        
        # 竞争机会
        competition = local_seo_data.get('local_competition', {})
        if competition.get('market_saturation') == 'low':
            opportunities.append({
                'type': 'market_opportunity',
                'title': '低竞争市场机会',
                'description': '当前市场竞争较小，是建立本地搜索优势的好时机',
                'potential_impact': 'high',
                'action_required': '加强本地SEO投入，快速占领市场'
            })
        
        # 评论机会
        reviews = local_seo_data.get('reviews_strategy', {})
        if len(reviews.get('current_reviews', {})) == 0:
            opportunities.append({
                'type': 'review_opportunity',
                'title': '建立评论基础',
                'description': '当前缺少在线评论，建立评论基础可以快速提升可信度',
                'potential_impact': 'medium',
                'action_required': '制定客户评论收集策略'
            })
        
        return opportunities
    
    async def _generate_local_keyword_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """使用AI生成本地关键词建议"""
        if not self.openai_service:
            return []
        
        prompt = f"""
        基于以下网站内容，生成10个本地SEO关键词建议，这些关键词应该：
        1. 包含地理位置修饰词
        2. 符合本地搜索习惯
        3. 具有商业价值
        4. 竞争相对较小
        
        网站内容：
        {content[:800]}
        
        请以JSON格式返回：
        {{
            "local_keywords": [
                {{
                    "keyword": "关键词",
                    "geo_modifier": "地理修饰词",
                    "search_intent": "informational/commercial/navigational",
                    "difficulty": "easy/medium/hard",
                    "reasoning": "推荐理由"
                }}
            ]
        }}
        """
        
        try:
            response = await self.openai_service.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            import json
            result = json.loads(response)
            return result.get('local_keywords', [])
            
        except Exception as e:
            logger.error(f"Local keyword generation failed: {str(e)}")
            return []
    
    def _estimate_tokens_used(self, local_seo_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 基于分析的复杂度估算
        base_tokens = 800
        if local_seo_data.get('local_keywords', {}).get('missing_local_keywords'):
            base_tokens += 500
        return base_tokens
    
    def _estimate_cost(self, local_seo_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(local_seo_data)
        # OpenAI + Google Places API 成本
        openai_cost = tokens / 1000 * 0.03
        places_cost = 0.005  # Google Places API 成本
        return openai_cost + places_cost
