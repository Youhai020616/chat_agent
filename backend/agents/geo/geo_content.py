"""
GeoContent Agent - 地理内容优化分析

功能：
1. 地理相关内容分析
2. 本地化内容策略
3. 地理关键词内容优化
4. 区域性内容机会识别
5. 多地区内容策略
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class GeoContentAgent(BaseAgent):
    """地理内容优化分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("geo_content", config)
        self.openai_service = OpenAIService(config)
        
        # 地理内容评估维度
        self.content_dimensions = {
            'location_relevance': {'weight': 0.25, 'max_score': 100},
            'local_keywords': {'weight': 0.20, 'max_score': 100},
            'regional_context': {'weight': 0.20, 'max_score': 100},
            'cultural_adaptation': {'weight': 0.15, 'max_score': 100},
            'local_events_trends': {'weight': 0.10, 'max_score': 100},
            'multi_location_strategy': {'weight': 0.10, 'max_score': 100}
        }
        
        # 地理内容类型
        self.geo_content_types = [
            'location_pages',      # 位置页面
            'service_area_pages',  # 服务区域页面
            'local_guides',        # 本地指南
            'regional_case_studies', # 区域案例研究
            'local_news_updates',  # 本地新闻更新
            'community_content'    # 社区内容
        ]
        
        # 中国主要城市和地区
        self.major_cities = [
            '北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉',
            '西安', '重庆', '天津', '青岛', '大连', '厦门', '苏州', '无锡'
        ]
        
        # 地理内容信号词
        self.geo_signals = [
            '位于', '坐落在', '服务于', '覆盖', '辐射', '周边',
            '当地', '本地', '附近', '就近', '区域', '地区'
        ]
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行地理内容优化分析"""
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
            keyword_insights = state.keyword_insights
            
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行地理内容分析任务
            tasks = [
                self._analyze_location_relevance(crawl_data, geo_insights),
                self._analyze_local_keyword_content(crawl_data, keyword_insights),
                self._analyze_regional_context(crawl_data, geo_insights),
                self._analyze_cultural_adaptation(crawl_data, state.locale),
                self._identify_content_gaps(crawl_data, geo_insights),
                self._generate_content_strategy(crawl_data, geo_insights, state.locale)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            geo_content_data = {
                'location_relevance': results[0] if not isinstance(results[0], Exception) else {},
                'local_keyword_content': results[1] if not isinstance(results[1], Exception) else {},
                'regional_context': results[2] if not isinstance(results[2], Exception) else {},
                'cultural_adaptation': results[3] if not isinstance(results[3], Exception) else {},
                'content_gaps': results[4] if not isinstance(results[4], Exception) else {},
                'content_strategy': results[5] if not isinstance(results[5], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算地理内容优化分数
            geo_content_data['geo_content_score'] = await self._calculate_geo_content_score(geo_content_data)
            
            # 生成地理内容优化建议
            geo_content_data['recommendations'] = await self._generate_geo_content_recommendations(geo_content_data)
            
            # 识别内容机会
            geo_content_data['content_opportunities'] = await self._identify_content_opportunities(geo_content_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=geo_content_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(geo_content_data),
                cost=self._estimate_cost(geo_content_data)
            )
            
        except Exception as e:
            logger.error(f"Geo content analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_location_relevance(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析位置相关性"""
        location_analysis = {
            'location_mentions': [],
            'geo_signal_density': 0,
            'location_context_score': 0,
            'missing_location_info': [],
            'location_distribution': {}
        }
        
        # 提取所有文本内容
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        if not all_text:
            return location_analysis
        
        # 统计地理信号词密度
        geo_signal_count = 0
        for signal in self.geo_signals:
            count = all_text.lower().count(signal)
            geo_signal_count += count
        
        total_words = len(all_text.split())
        location_analysis['geo_signal_density'] = (geo_signal_count / total_words * 100) if total_words > 0 else 0
        
        # 识别位置提及
        if geo_insights:
            geographic_entities = geo_insights.get('geographic_entities', {})
            
            for entity_type, entities in geographic_entities.items():
                for entity in entities:
                    if entity in all_text:
                        location_analysis['location_mentions'].append({
                            'location': entity,
                            'type': entity_type,
                            'context': self._extract_location_context(all_text, entity)
                        })
        
        # 分析位置分布
        city_mentions = Counter()
        for city in self.major_cities:
            count = all_text.count(city)
            if count > 0:
                city_mentions[city] = count
        
        location_analysis['location_distribution'] = dict(city_mentions.most_common(10))
        
        # 计算位置上下文分数
        context_score = 0
        if location_analysis['location_mentions']:
            context_score += 30
        if location_analysis['geo_signal_density'] > 1.0:
            context_score += 25
        if location_analysis['location_distribution']:
            context_score += 25
        if geo_insights and geo_insights.get('business_entities', {}).get('contact_info', {}).get('address'):
            context_score += 20
        
        location_analysis['location_context_score'] = context_score
        
        return location_analysis
    
    async def _analyze_local_keyword_content(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析本地关键词内容"""
        keyword_content_analysis = {
            'local_keyword_usage': [],
            'keyword_context_quality': {},
            'missing_local_keywords': [],
            'keyword_content_score': 0
        }
        
        if not keyword_insights:
            return keyword_content_analysis
        
        # 获取当前关键词
        current_keywords = keyword_insights.get('current_keywords', [])
        
        # 分析本地关键词使用情况
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        local_keywords_found = []
        for kw_data in current_keywords:
            keyword = kw_data.get('keyword', '')
            
            # 检查是否为本地关键词
            is_local = any(geo_signal in keyword.lower() for geo_signal in self.geo_signals)
            is_local = is_local or any(city in keyword for city in self.major_cities)
            
            if is_local:
                context = self._extract_keyword_context(all_text, keyword)
                local_keywords_found.append({
                    'keyword': keyword,
                    'frequency': kw_data.get('frequency', 0),
                    'context_quality': self._assess_context_quality(context),
                    'context': context
                })
        
        keyword_content_analysis['local_keyword_usage'] = local_keywords_found
        
        # 计算关键词内容分数
        if local_keywords_found:
            avg_quality = sum(kw['context_quality'] for kw in local_keywords_found) / len(local_keywords_found)
            keyword_content_analysis['keyword_content_score'] = int(avg_quality)
        
        return keyword_content_analysis
    
    async def _analyze_regional_context(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析区域背景"""
        regional_analysis = {
            'regional_relevance': 0,
            'market_context': {},
            'regional_competitors': [],
            'local_market_insights': []
        }
        
        # 基于地理实体分析区域相关性
        if geo_insights:
            geographic_entities = geo_insights.get('geographic_entities', {})
            
            # 计算区域相关性分数
            relevance_score = 0
            if geographic_entities.get('cities'):
                relevance_score += 30
            if geographic_entities.get('provinces'):
                relevance_score += 25
            if geographic_entities.get('districts'):
                relevance_score += 20
            if geographic_entities.get('landmarks'):
                relevance_score += 25
            
            regional_analysis['regional_relevance'] = relevance_score
            
            # 分析市场背景
            if geographic_entities.get('cities'):
                primary_city = geographic_entities['cities'][0]
                regional_analysis['market_context'] = {
                    'primary_market': primary_city,
                    'market_type': self._classify_market_type(primary_city),
                    'market_characteristics': self._get_market_characteristics(primary_city)
                }
        
        return regional_analysis
    
    async def _analyze_cultural_adaptation(self, crawl_data: Dict[str, Any], locale: str) -> Dict[str, Any]:
        """分析文化适应性"""
        cultural_analysis = {
            'language_adaptation': 0,
            'cultural_elements': [],
            'localization_score': 0,
            'improvement_suggestions': []
        }
        
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        # 分析语言适应性
        if locale.startswith('zh'):
            # 中文本地化检查
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', all_text))
            total_chars = len(all_text)
            
            if total_chars > 0:
                chinese_ratio = chinese_chars / total_chars
                cultural_analysis['language_adaptation'] = int(chinese_ratio * 100)
            
            # 检查文化元素
            cultural_keywords = ['中国', '中华', '传统', '文化', '节日', '习俗']
            for keyword in cultural_keywords:
                if keyword in all_text:
                    cultural_analysis['cultural_elements'].append(keyword)
        
        # 计算本地化分数
        localization_score = cultural_analysis['language_adaptation']
        if cultural_analysis['cultural_elements']:
            localization_score += min(20, len(cultural_analysis['cultural_elements']) * 5)
        
        cultural_analysis['localization_score'] = min(100, localization_score)
        
        return cultural_analysis
    
    async def _identify_content_gaps(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别内容缺口"""
        content_gaps = []
        
        # 检查位置页面缺口
        if not geo_insights or not geo_insights.get('geographic_entities', {}).get('cities'):
            content_gaps.append({
                'gap_type': 'location_pages',
                'priority': 'high',
                'description': '缺少具体的位置页面',
                'recommendation': '为主要服务城市创建专门的位置页面'
            })
        
        # 检查服务区域内容缺口
        service_areas = geo_insights.get('service_areas', []) if geo_insights else []
        if not service_areas:
            content_gaps.append({
                'gap_type': 'service_area_content',
                'priority': 'medium',
                'description': '缺少服务区域说明',
                'recommendation': '明确说明服务覆盖的地理区域'
            })
        
        # 检查本地指南缺口
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', '')
        ])
        
        if '指南' not in all_text and '攻略' not in all_text:
            content_gaps.append({
                'gap_type': 'local_guides',
                'priority': 'low',
                'description': '缺少本地指南内容',
                'recommendation': '创建本地相关的指南或攻略内容'
            })
        
        return content_gaps
    
    async def _generate_content_strategy(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]], locale: str) -> Dict[str, Any]:
        """生成内容策略"""
        content_strategy = {
            'content_pillars': [],
            'content_calendar': {},
            'target_locations': [],
            'content_types': [],
            'distribution_strategy': {}
        }
        
        # 基于地理洞察确定目标位置
        if geo_insights:
            geographic_entities = geo_insights.get('geographic_entities', {})
            cities = geographic_entities.get('cities', [])
            provinces = geographic_entities.get('provinces', [])
            
            content_strategy['target_locations'] = cities + provinces
        
        # 使用AI生成内容策略
        if self.openai_service and self.openai_service.is_available():
            try:
                ai_strategy = await self._generate_ai_content_strategy(crawl_data, geo_insights, locale)
                content_strategy.update(ai_strategy)
            except Exception as e:
                logger.warning(f"AI content strategy generation failed: {str(e)}")
        
        # 默认内容类型
        content_strategy['content_types'] = self.geo_content_types
        
        return content_strategy
    
    async def _calculate_geo_content_score(self, geo_content_data: Dict[str, Any]) -> int:
        """计算地理内容优化分数"""
        total_score = 0
        
        for dimension, config in self.content_dimensions.items():
            dimension_score = 0
            
            if dimension == 'location_relevance':
                location_data = geo_content_data.get('location_relevance', {})
                dimension_score = location_data.get('location_context_score', 0)
            
            elif dimension == 'local_keywords':
                keyword_data = geo_content_data.get('local_keyword_content', {})
                dimension_score = keyword_data.get('keyword_content_score', 0)
            
            elif dimension == 'regional_context':
                regional_data = geo_content_data.get('regional_context', {})
                dimension_score = regional_data.get('regional_relevance', 0)
            
            elif dimension == 'cultural_adaptation':
                cultural_data = geo_content_data.get('cultural_adaptation', {})
                dimension_score = cultural_data.get('localization_score', 0)
            
            elif dimension == 'local_events_trends':
                # 暂时使用默认分数
                dimension_score = 50
            
            elif dimension == 'multi_location_strategy':
                # 基于目标位置数量评分
                strategy_data = geo_content_data.get('content_strategy', {})
                target_locations = strategy_data.get('target_locations', [])
                dimension_score = min(100, len(target_locations) * 20)
            
            # 加权计算
            weighted_score = dimension_score * config['weight']
            total_score += weighted_score
        
        return int(total_score)
    
    async def _generate_geo_content_recommendations(self, geo_content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成地理内容优化建议"""
        recommendations = []
        
        # 基于位置相关性生成建议
        location_data = geo_content_data.get('location_relevance', {})
        if location_data.get('location_context_score', 0) < 60:
            recommendations.append({
                'category': 'location_content',
                'priority': 'high',
                'title': '增强位置相关性',
                'description': '在内容中增加更多地理位置信息和本地化元素',
                'impact': 4,
                'effort': 3
            })
        
        # 基于关键词内容生成建议
        keyword_data = geo_content_data.get('local_keyword_content', {})
        if keyword_data.get('keyword_content_score', 0) < 70:
            recommendations.append({
                'category': 'local_keywords',
                'priority': 'medium',
                'title': '优化本地关键词使用',
                'description': '在内容中更自然地融入本地关键词',
                'impact': 3,
                'effort': 2
            })
        
        # 基于内容缺口生成建议
        content_gaps = geo_content_data.get('content_gaps', [])
        for gap in content_gaps[:3]:  # 只处理前3个缺口
            recommendations.append({
                'category': 'content_gaps',
                'priority': gap.get('priority', 'medium'),
                'title': f'填补{gap.get("gap_type", "内容")}缺口',
                'description': gap.get('recommendation', ''),
                'impact': 3,
                'effort': 3
            })
        
        return recommendations
    
    async def _identify_content_opportunities(self, geo_content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别内容机会"""
        opportunities = []
        
        # 多地区扩展机会
        strategy_data = geo_content_data.get('content_strategy', {})
        target_locations = strategy_data.get('target_locations', [])
        
        if len(target_locations) < 3:
            opportunities.append({
                'type': 'geographic_expansion',
                'title': '地理扩展机会',
                'description': '可以扩展到更多地理区域，增加市场覆盖',
                'potential_impact': 'medium',
                'action_required': '研究新的目标市场并创建相应内容'
            })
        
        # 本地合作机会
        regional_data = geo_content_data.get('regional_context', {})
        if regional_data.get('regional_relevance', 0) > 70:
            opportunities.append({
                'type': 'local_partnerships',
                'title': '本地合作机会',
                'description': '与本地企业或组织合作，创建联合内容',
                'potential_impact': 'high',
                'action_required': '寻找本地合作伙伴并制定合作内容计划'
            })
        
        return opportunities
    
    def _extract_location_context(self, text: str, location: str) -> str:
        """提取位置上下文"""
        # 查找包含位置的句子
        sentences = text.split('。')
        for sentence in sentences:
            if location in sentence:
                return sentence.strip()
        return ""
    
    def _extract_keyword_context(self, text: str, keyword: str) -> str:
        """提取关键词上下文"""
        # 查找包含关键词的句子
        sentences = text.split('。')
        for sentence in sentences:
            if keyword in sentence:
                return sentence.strip()
        return ""
    
    def _assess_context_quality(self, context: str) -> int:
        """评估上下文质量"""
        if not context:
            return 0
        
        quality_score = 50  # 基础分数
        
        # 长度评估
        if len(context) > 20:
            quality_score += 20
        
        # 信息丰富度评估
        if any(signal in context for signal in self.geo_signals):
            quality_score += 15
        
        # 专业性评估
        professional_words = ['服务', '专业', '优质', '经验', '团队']
        if any(word in context for word in professional_words):
            quality_score += 15
        
        return min(100, quality_score)
    
    def _classify_market_type(self, city: str) -> str:
        """分类市场类型"""
        tier1_cities = ['北京', '上海', '广州', '深圳']
        tier2_cities = ['杭州', '南京', '成都', '武汉', '西安', '重庆']
        
        if city in tier1_cities:
            return 'tier1'
        elif city in tier2_cities:
            return 'tier2'
        else:
            return 'tier3'
    
    def _get_market_characteristics(self, city: str) -> List[str]:
        """获取市场特征"""
        market_chars = {
            '北京': ['政治中心', '高科技', '教育资源丰富'],
            '上海': ['金融中心', '国际化', '商业发达'],
            '广州': ['商贸中心', '制造业', '交通枢纽'],
            '深圳': ['科技创新', '年轻化', '创业氛围'],
            '杭州': ['电商中心', '互联网', '宜居城市']
        }
        
        return market_chars.get(city, ['发展中市场', '潜力巨大'])
    
    async def _generate_ai_content_strategy(self, crawl_data: Dict[str, Any], geo_insights: Optional[Dict[str, Any]], locale: str) -> Dict[str, Any]:
        """使用AI生成内容策略"""
        if not self.openai_service:
            return {}
        
        content = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', '')
        ])
        
        geo_context = ""
        if geo_insights:
            geographic_entities = geo_insights.get('geographic_entities', {})
            geo_context = f"地理实体: {geographic_entities}"
        
        prompt = f"""
        基于以下信息，为企业制定地理内容策略：
        
        企业信息：{content[:500]}
        地理背景：{geo_context[:300]}
        目标市场：{locale}
        
        请生成包含以下内容的策略：
        1. 3-5个内容支柱主题
        2. 月度内容日历建议
        3. 内容分发策略
        
        以JSON格式返回：
        {{
            "content_pillars": ["主题1", "主题2", "主题3"],
            "content_calendar": {{
                "monthly_themes": ["1月主题", "2月主题"],
                "posting_frequency": "建议频率"
            }},
            "distribution_strategy": {{
                "primary_channels": ["渠道1", "渠道2"],
                "content_formats": ["格式1", "格式2"]
            }}
        }}
        """
        
        try:
            response = await self.openai_service.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            import json
            result = json.loads(response)
            return result
            
        except Exception as e:
            logger.error(f"AI content strategy generation failed: {str(e)}")
            return {}
    
    def _estimate_tokens_used(self, geo_content_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        base_tokens = 700
        if geo_content_data.get('content_strategy', {}).get('content_pillars'):
            base_tokens += 600
        return base_tokens
    
    def _estimate_cost(self, geo_content_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(geo_content_data)
        return tokens / 1000 * 0.03
