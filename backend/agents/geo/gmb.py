"""
GMB Agent - Google My Business 优化分析

功能：
1. GMB 档案完整性检查
2. GMB 内容优化分析
3. 客户评论管理策略
4. GMB 帖子和更新策略
5. GMB 性能指标分析
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService
from ...services.external.google_places import GooglePlacesService

logger = logging.getLogger(__name__)


class GMBAgent(BaseAgent):
    """Google My Business 优化分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("gmb", config)
        self.openai_service = OpenAIService(config)
        self.places_service = GooglePlacesService(config)
        
        # GMB 优化评估标准
        self.gmb_factors = {
            'basic_info': {
                'weight': 0.25,
                'fields': ['name', 'address', 'phone', 'website', 'category']
            },
            'detailed_info': {
                'weight': 0.20,
                'fields': ['description', 'hours', 'attributes', 'photos']
            },
            'customer_engagement': {
                'weight': 0.25,
                'fields': ['reviews', 'q_and_a', 'messages', 'posts']
            },
            'content_quality': {
                'weight': 0.15,
                'fields': ['photos_quality', 'description_quality', 'posts_quality']
            },
            'performance_metrics': {
                'weight': 0.15,
                'fields': ['views', 'actions', 'calls', 'direction_requests']
            }
        }
        
        # GMB 帖子类型
        self.gmb_post_types = [
            'what_is_new',  # 最新动态
            'event',        # 活动
            'offer',        # 优惠
            'product'       # 产品
        ]
        
        # 重要的 GMB 属性
        self.important_attributes = [
            'wheelchair_accessible',
            'free_wifi',
            'accepts_credit_cards',
            'parking_available',
            'appointment_required',
            'online_service_available'
        ]
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行 GMB 优化分析"""
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
            
            # 并行执行 GMB 分析任务
            tasks = [
                self._analyze_gmb_completeness(crawl_data, geo_insights),
                self._analyze_gmb_content_quality(geo_insights),
                self._analyze_customer_engagement(geo_insights),
                self._analyze_gmb_performance(geo_insights),
                self._analyze_competitor_gmb(state.target_url, state.locale),
                self._generate_gmb_content_strategy(crawl_data, geo_insights)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            gmb_data = {
                'completeness_analysis': results[0] if not isinstance(results[0], Exception) else {},
                'content_quality': results[1] if not isinstance(results[1], Exception) else {},
                'customer_engagement': results[2] if not isinstance(results[2], Exception) else {},
                'performance_analysis': results[3] if not isinstance(results[3], Exception) else {},
                'competitor_analysis': results[4] if not isinstance(results[4], Exception) else {},
                'content_strategy': results[5] if not isinstance(results[5], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算 GMB 优化分数
            gmb_data['gmb_optimization_score'] = await self._calculate_gmb_score(gmb_data)
            
            # 生成 GMB 优化建议
            gmb_data['recommendations'] = await self._generate_gmb_recommendations(gmb_data)
            
            # 识别 GMB 优化机会
            gmb_data['optimization_opportunities'] = await self._identify_gmb_opportunities(gmb_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=gmb_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(gmb_data),
                cost=self._estimate_cost(gmb_data)
            )
            
        except Exception as e:
            logger.error(f"GMB analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_gmb_completeness(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析 GMB 档案完整性"""
        completeness = {
            'overall_score': 0,
            'basic_info_score': 0,
            'detailed_info_score': 0,
            'missing_fields': [],
            'completed_fields': [],
            'field_analysis': {}
        }
        
        # 从 schema 数据中提取 GMB 信息
        gmb_info = {}
        if geo_insights:
            schema_entities = geo_insights.get('schema_entities', {})
            organizations = schema_entities.get('organizations', [])
            
            for org in organizations:
                if org.get('name') and org.get('address'):
                    gmb_info = org
                    break
        
        # 分析基础信息完整性
        basic_fields = self.gmb_factors['basic_info']['fields']
        basic_score = 0
        
        for field in basic_fields:
            field_data = {
                'field': field,
                'present': False,
                'quality': 'unknown',
                'recommendations': []
            }
            
            if field == 'name' and gmb_info.get('name'):
                field_data['present'] = True
                name = gmb_info['name']
                if len(name) > 50:
                    field_data['quality'] = 'poor'
                    field_data['recommendations'].append('企业名称过长，建议简化')
                else:
                    field_data['quality'] = 'good'
                basic_score += 20
                completeness['completed_fields'].append(field)
            
            elif field == 'address' and gmb_info.get('address'):
                field_data['present'] = True
                field_data['quality'] = 'good'
                basic_score += 20
                completeness['completed_fields'].append(field)
            
            elif field == 'phone' and gmb_info.get('telephone'):
                field_data['present'] = True
                field_data['quality'] = 'good'
                basic_score += 20
                completeness['completed_fields'].append(field)
            
            elif field == 'website' and gmb_info.get('url'):
                field_data['present'] = True
                field_data['quality'] = 'good'
                basic_score += 20
                completeness['completed_fields'].append(field)
            
            elif field == 'category':
                # 从 schema type 推断类别
                if gmb_info.get('@type'):
                    field_data['present'] = True
                    field_data['quality'] = 'good'
                    basic_score += 20
                    completeness['completed_fields'].append(field)
            
            if not field_data['present']:
                completeness['missing_fields'].append(field)
            
            completeness['field_analysis'][field] = field_data
        
        completeness['basic_info_score'] = basic_score
        
        # 分析详细信息完整性
        detailed_fields = self.gmb_factors['detailed_info']['fields']
        detailed_score = 0
        
        for field in detailed_fields:
            field_data = {
                'field': field,
                'present': False,
                'quality': 'unknown',
                'recommendations': []
            }
            
            if field == 'description':
                # 从网站内容推断是否有描述
                meta_desc = crawl_data.get('meta_description')
                if meta_desc and len(meta_desc) > 50:
                    field_data['present'] = True
                    field_data['quality'] = 'good'
                    detailed_score += 25
                else:
                    field_data['recommendations'].append('添加详细的企业描述')
            
            elif field == 'hours':
                # 检查是否有营业时间信息
                all_text = ' '.join([
                    crawl_data.get('title', ''),
                    crawl_data.get('meta_description', ''),
                    ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
                ])
                
                if re.search(r'营业|开放|工作时间|小时', all_text, re.IGNORECASE):
                    field_data['present'] = True
                    field_data['quality'] = 'good'
                    detailed_score += 25
                else:
                    field_data['recommendations'].append('添加营业时间信息')
            
            elif field == 'attributes':
                # 检查是否有属性信息
                if re.search(r'wifi|停车|轮椅|信用卡', all_text, re.IGNORECASE):
                    field_data['present'] = True
                    field_data['quality'] = 'partial'
                    detailed_score += 15
                else:
                    field_data['recommendations'].append('添加企业属性信息')
            
            elif field == 'photos':
                # 检查是否有图片
                images = crawl_data.get('images', [])
                if len(images) > 0:
                    field_data['present'] = True
                    if len(images) >= 5:
                        field_data['quality'] = 'good'
                        detailed_score += 25
                    else:
                        field_data['quality'] = 'partial'
                        detailed_score += 15
                        field_data['recommendations'].append('增加更多高质量照片')
                else:
                    field_data['recommendations'].append('添加企业照片')
            
            completeness['field_analysis'][field] = field_data
        
        completeness['detailed_info_score'] = detailed_score
        completeness['overall_score'] = (basic_score + detailed_score) / 2
        
        return completeness
    
    async def _analyze_gmb_content_quality(self, geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析 GMB 内容质量"""
        content_quality = {
            'description_quality': 0,
            'photos_quality': 0,
            'overall_content_score': 0,
            'content_issues': [],
            'improvement_suggestions': []
        }
        
        if not geo_insights:
            return content_quality
        
        # 分析描述质量
        business_entities = geo_insights.get('business_entities', {})
        if business_entities.get('company_names'):
            # 模拟描述质量分析
            content_quality['description_quality'] = 75
            content_quality['improvement_suggestions'].append({
                'area': 'description',
                'suggestion': '在描述中添加更多关键词和服务详情',
                'priority': 'medium'
            })
        
        # 分析照片质量
        # 这里需要实际的照片分析，暂时使用模拟数据
        content_quality['photos_quality'] = 60
        content_quality['improvement_suggestions'].append({
            'area': 'photos',
            'suggestion': '添加更多展示企业内外环境的高质量照片',
            'priority': 'high'
        })
        
        content_quality['overall_content_score'] = (
            content_quality['description_quality'] + 
            content_quality['photos_quality']
        ) / 2
        
        return content_quality
    
    async def _analyze_customer_engagement(self, geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析客户互动情况"""
        engagement = {
            'reviews_analysis': {},
            'qa_analysis': {},
            'messaging_analysis': {},
            'posts_analysis': {},
            'engagement_score': 0,
            'engagement_opportunities': []
        }
        
        # 模拟评论分析
        engagement['reviews_analysis'] = {
            'total_reviews': 0,
            'average_rating': 0,
            'recent_reviews': 0,
            'response_rate': 0,
            'sentiment_analysis': 'neutral'
        }
        
        # 模拟问答分析
        engagement['qa_analysis'] = {
            'total_questions': 0,
            'answered_questions': 0,
            'response_time': 'unknown',
            'answer_quality': 'unknown'
        }
        
        # 模拟消息分析
        engagement['messaging_analysis'] = {
            'messaging_enabled': False,
            'response_rate': 0,
            'average_response_time': 'unknown'
        }
        
        # 模拟帖子分析
        engagement['posts_analysis'] = {
            'total_posts': 0,
            'recent_posts': 0,
            'post_types': [],
            'engagement_rate': 0
        }
        
        # 识别互动机会
        engagement['engagement_opportunities'] = [
            {
                'opportunity': 'enable_messaging',
                'description': '启用消息功能，提供即时客户服务',
                'impact': 'medium',
                'effort': 'low'
            },
            {
                'opportunity': 'regular_posts',
                'description': '定期发布GMB帖子，保持活跃度',
                'impact': 'medium',
                'effort': 'medium'
            }
        ]
        
        return engagement
    
    async def _analyze_gmb_performance(self, geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析 GMB 性能指标"""
        performance = {
            'visibility_metrics': {},
            'action_metrics': {},
            'trend_analysis': {},
            'performance_score': 0,
            'improvement_areas': []
        }
        
        # 模拟性能数据（实际需要从 GMB API 获取）
        performance['visibility_metrics'] = {
            'search_views': 0,
            'maps_views': 0,
            'total_views': 0,
            'view_trend': 'unknown'
        }
        
        performance['action_metrics'] = {
            'website_clicks': 0,
            'direction_requests': 0,
            'phone_calls': 0,
            'total_actions': 0,
            'conversion_rate': 0
        }
        
        performance['improvement_areas'] = [
            {
                'area': 'visibility',
                'current_score': 0,
                'target_score': 80,
                'recommendations': ['优化GMB档案完整性', '增加客户评论']
            },
            {
                'area': 'engagement',
                'current_score': 0,
                'target_score': 70,
                'recommendations': ['定期发布更新', '回复客户评论']
            }
        ]
        
        return performance
    
    async def _analyze_competitor_gmb(self, target_url: str, locale: str) -> Dict[str, Any]:
        """分析竞争对手 GMB 策略"""
        competitor_analysis = {
            'competitor_profiles': [],
            'competitive_gaps': [],
            'competitive_advantages': [],
            'benchmarking': {}
        }
        
        if not self.places_service or not self.places_service.is_available():
            return competitor_analysis
        
        try:
            # 基于业务类型查找竞争对手
            business_type = "SEO服务"  # 示例
            location = "北京"  # 示例
            
            competitors = await self.places_service.search_nearby(location, 5000, "establishment", business_type)
            
            for competitor in competitors[:3]:  # 分析前3个竞争对手
                competitor_profile = {
                    'name': competitor.get('name', ''),
                    'rating': competitor.get('rating', 0),
                    'reviews_count': competitor.get('user_ratings_total', 0),
                    'place_id': competitor.get('place_id', ''),
                    'strengths': [],
                    'weaknesses': []
                }
                
                # 分析竞争对手优势
                if competitor_profile['rating'] > 4.0:
                    competitor_profile['strengths'].append('高客户评分')
                
                if competitor_profile['reviews_count'] > 50:
                    competitor_profile['strengths'].append('大量客户评论')
                
                competitor_analysis['competitor_profiles'].append(competitor_profile)
            
            # 识别竞争差距
            if competitors:
                avg_rating = sum(c.get('rating', 0) for c in competitors) / len(competitors)
                avg_reviews = sum(c.get('user_ratings_total', 0) for c in competitors) / len(competitors)
                
                competitor_analysis['benchmarking'] = {
                    'average_competitor_rating': avg_rating,
                    'average_competitor_reviews': avg_reviews,
                    'market_position': 'needs_improvement'  # 基于比较结果
                }
        
        except Exception as e:
            logger.error(f"Competitor GMB analysis failed: {str(e)}")
        
        return competitor_analysis
    
    async def _generate_gmb_content_strategy(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成 GMB 内容策略"""
        content_strategy = {
            'posting_schedule': {},
            'content_themes': [],
            'photo_strategy': {},
            'engagement_strategy': {},
            'monthly_plan': []
        }
        
        # 生成发布计划
        content_strategy['posting_schedule'] = {
            'frequency': 'weekly',
            'best_times': ['周二 10:00', '周四 14:00', '周六 11:00'],
            'post_types_rotation': self.gmb_post_types
        }
        
        # 内容主题建议
        if self.openai_service and self.openai_service.is_available():
            try:
                themes = await self._generate_content_themes(crawl_data)
                content_strategy['content_themes'] = themes
            except Exception as e:
                logger.warning(f"Content theme generation failed: {str(e)}")
        
        # 照片策略
        content_strategy['photo_strategy'] = {
            'required_photos': [
                '企业外观', '企业内部', '团队照片', '服务过程', '客户案例'
            ],
            'photo_schedule': '每月至少添加2张新照片',
            'quality_requirements': '高分辨率、良好光线、专业构图'
        }
        
        # 互动策略
        content_strategy['engagement_strategy'] = {
            'review_response': '24小时内回复所有评论',
            'qa_management': '及时回答客户问题',
            'messaging': '启用消息功能并快速回复'
        }
        
        return content_strategy
    
    async def _calculate_gmb_score(self, gmb_data: Dict[str, Any]) -> int:
        """计算 GMB 优化分数"""
        total_score = 0
        
        # 基础信息分数 (25%)
        completeness = gmb_data.get('completeness_analysis', {})
        basic_score = completeness.get('basic_info_score', 0)
        total_score += basic_score * 0.25
        
        # 详细信息分数 (20%)
        detailed_score = completeness.get('detailed_info_score', 0)
        total_score += detailed_score * 0.20
        
        # 客户互动分数 (25%)
        engagement = gmb_data.get('customer_engagement', {})
        engagement_score = engagement.get('engagement_score', 0)
        total_score += engagement_score * 0.25
        
        # 内容质量分数 (15%)
        content_quality = gmb_data.get('content_quality', {})
        content_score = content_quality.get('overall_content_score', 0)
        total_score += content_score * 0.15
        
        # 性能指标分数 (15%)
        performance = gmb_data.get('performance_analysis', {})
        performance_score = performance.get('performance_score', 0)
        total_score += performance_score * 0.15
        
        return int(total_score)
    
    async def _generate_gmb_recommendations(self, gmb_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成 GMB 优化建议"""
        recommendations = []
        
        # 基于完整性分析生成建议
        completeness = gmb_data.get('completeness_analysis', {})
        missing_fields = completeness.get('missing_fields', [])
        
        if 'name' in missing_fields:
            recommendations.append({
                'category': 'basic_setup',
                'priority': 'critical',
                'title': '添加企业名称',
                'description': '企业名称是GMB档案的核心，必须准确填写',
                'impact': 5,
                'effort': 1
            })
        
        if 'description' in missing_fields:
            recommendations.append({
                'category': 'content',
                'priority': 'high',
                'title': '添加企业描述',
                'description': '详细的企业描述有助于客户了解您的业务',
                'impact': 4,
                'effort': 2
            })
        
        # 基于内容质量生成建议
        content_quality = gmb_data.get('content_quality', {})
        if content_quality.get('photos_quality', 0) < 70:
            recommendations.append({
                'category': 'photos',
                'priority': 'medium',
                'title': '改善照片质量',
                'description': '上传更多高质量的企业照片，展示您的业务',
                'impact': 3,
                'effort': 3
            })
        
        return recommendations
    
    async def _identify_gmb_opportunities(self, gmb_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别 GMB 优化机会"""
        opportunities = []
        
        # 竞争机会
        competitor_analysis = gmb_data.get('competitor_analysis', {})
        benchmarking = competitor_analysis.get('benchmarking', {})
        
        if benchmarking.get('market_position') == 'needs_improvement':
            opportunities.append({
                'type': 'competitive_advantage',
                'title': '超越竞争对手',
                'description': '通过完善GMB档案和积极互动，可以超越当前竞争对手',
                'potential_impact': 'high',
                'action_required': '全面优化GMB档案并建立评论收集策略'
            })
        
        # 内容机会
        content_strategy = gmb_data.get('content_strategy', {})
        if content_strategy.get('content_themes'):
            opportunities.append({
                'type': 'content_marketing',
                'title': '内容营销机会',
                'description': '通过定期发布有价值的内容，提升客户参与度',
                'potential_impact': 'medium',
                'action_required': '制定并执行内容发布计划'
            })
        
        return opportunities
    
    async def _generate_content_themes(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用AI生成内容主题"""
        if not self.openai_service:
            return []
        
        content = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', '')
        ])
        
        prompt = f"""
        基于以下企业信息，为Google My Business生成5个内容主题，每个主题应该：
        1. 与企业业务相关
        2. 能够吸引客户参与
        3. 适合定期发布
        4. 有助于建立专业形象
        
        企业信息：
        {content[:500]}
        
        请以JSON格式返回：
        {{
            "content_themes": [
                {{
                    "theme": "主题名称",
                    "description": "主题描述",
                    "post_frequency": "发布频率",
                    "example_content": "示例内容"
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
            return result.get('content_themes', [])
            
        except Exception as e:
            logger.error(f"Content theme generation failed: {str(e)}")
            return []
    
    def _estimate_tokens_used(self, gmb_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        base_tokens = 600
        if gmb_data.get('content_strategy', {}).get('content_themes'):
            base_tokens += 400
        return base_tokens
    
    def _estimate_cost(self, gmb_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(gmb_data)
        # OpenAI + Google Places API 成本
        openai_cost = tokens / 1000 * 0.03
        places_cost = 0.003  # Google Places API 成本
        return openai_cost + places_cost
