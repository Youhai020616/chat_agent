"""
KeywordGap Agent - 关键词缺口分析

功能：
1. 分析网站当前关键词覆盖情况
2. 识别竞争对手的关键词策略
3. 发现关键词机会和缺口
4. 评估关键词难度和潜在价值
5. 生成关键词扩展建议
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from collections import Counter
import re

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService
from ...services.external.serp_api import SERPAPIService

logger = logging.getLogger(__name__)


class KeywordGapAgent(BaseAgent):
    """关键词缺口分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("keyword_gap", config)
        self.openai_service = OpenAIService(config)
        self.serp_api = SERPAPIService(config)
        
        # 关键词分析配置
        self.keyword_config = {
            'min_keyword_length': 2,
            'max_keyword_length': 50,
            'min_search_volume': 10,
            'max_keywords_to_analyze': 50,
            'competitor_analysis_limit': 5
        }
        
        # 关键词难度评估标准
        self.difficulty_thresholds = {
            'easy': {'competition': 0.3, 'domain_authority': 30},
            'medium': {'competition': 0.6, 'domain_authority': 60},
            'hard': {'competition': 0.8, 'domain_authority': 80}
        }
        
        # 停用词列表
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行关键词缺口分析"""
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(state):
                return AgentResult(
                    success=False,
                    data={},
                    error="Invalid input state"
                )
            
            # 获取爬虫数据
            crawl_data = state.crawl_data
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行关键词分析任务
            tasks = [
                self._extract_current_keywords(crawl_data),
                self._analyze_keyword_density(crawl_data),
                self._identify_semantic_keywords(crawl_data),
                self._analyze_competitor_keywords(state.target_url, state.locale),
                self._discover_keyword_opportunities(crawl_data, state.locale)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            keyword_data = {
                'current_keywords': results[0] if not isinstance(results[0], Exception) else [],
                'keyword_density': results[1] if not isinstance(results[1], Exception) else {},
                'semantic_keywords': results[2] if not isinstance(results[2], Exception) else [],
                'competitor_keywords': results[3] if not isinstance(results[3], Exception) else {},
                'keyword_opportunities': results[4] if not isinstance(results[4], Exception) else [],
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale,
                    'total_keywords_found': 0
                }
            }
            
            # 计算总关键词数量
            keyword_data['analysis_metadata']['total_keywords_found'] = len(keyword_data['current_keywords'])
            
            # 执行关键词缺口分析
            keyword_data['keyword_gaps'] = await self._identify_keyword_gaps(keyword_data)
            
            # 生成关键词策略建议
            keyword_data['keyword_strategy'] = await self._generate_keyword_strategy(keyword_data)
            
            # 评估关键词优先级
            keyword_data['priority_keywords'] = await self._prioritize_keywords(keyword_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=keyword_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(keyword_data),
                cost=self._estimate_cost(keyword_data)
            )
            
        except Exception as e:
            logger.error(f"Keyword gap analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _extract_current_keywords(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取当前页面的关键词"""
        keywords = []
        
        # 从不同来源提取关键词
        sources = {
            'title': crawl_data.get('title', ''),
            'meta_description': crawl_data.get('meta_description', ''),
            'meta_keywords': crawl_data.get('meta_keywords', ''),
            'headings': ' '.join([
                ' '.join(texts) for texts in crawl_data.get('headings', {}).values()
            ]),
            'image_alts': ' '.join([
                img.get('alt', '') for img in crawl_data.get('images', [])
            ]),
            'link_texts': ' '.join([
                link.get('text', '') for link in crawl_data.get('links', [])
            ])
        }
        
        # 处理每个来源的文本
        for source, text in sources.items():
            if text:
                source_keywords = self._extract_keywords_from_text(text, source)
                keywords.extend(source_keywords)
        
        # 去重并排序
        keyword_dict = {}
        for kw in keywords:
            key = kw['keyword'].lower()
            if key in keyword_dict:
                keyword_dict[key]['frequency'] += kw['frequency']
                keyword_dict[key]['sources'].extend(kw['sources'])
                keyword_dict[key]['sources'] = list(set(keyword_dict[key]['sources']))
            else:
                keyword_dict[key] = kw
        
        # 转换回列表并按频率排序
        final_keywords = list(keyword_dict.values())
        final_keywords.sort(key=lambda x: x['frequency'], reverse=True)
        
        return final_keywords[:self.keyword_config['max_keywords_to_analyze']]
    
    def _extract_keywords_from_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """从文本中提取关键词"""
        keywords = []
        
        # 清理文本
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)  # 保留中文字符
        words = text.lower().split()
        
        # 过滤停用词和短词
        filtered_words = [
            word for word in words 
            if word not in self.stop_words 
            and len(word) >= self.keyword_config['min_keyword_length']
            and len(word) <= self.keyword_config['max_keyword_length']
        ]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 生成单词关键词
        for word, count in word_counts.items():
            keywords.append({
                'keyword': word,
                'frequency': count,
                'sources': [source],
                'type': 'single_word',
                'length': len(word)
            })
        
        # 生成短语关键词（2-3个词）
        for phrase_length in [2, 3]:
            phrases = []
            for i in range(len(filtered_words) - phrase_length + 1):
                phrase = ' '.join(filtered_words[i:i + phrase_length])
                phrases.append(phrase)
            
            phrase_counts = Counter(phrases)
            for phrase, count in phrase_counts.items():
                if count > 1:  # 只保留出现多次的短语
                    keywords.append({
                        'keyword': phrase,
                        'frequency': count,
                        'sources': [source],
                        'type': 'phrase',
                        'length': len(phrase)
                    })
        
        return keywords
    
    async def _analyze_keyword_density(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析关键词密度"""
        # 合并所有文本内容
        all_text = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        if not all_text:
            return {'total_words': 0, 'keyword_densities': {}}
        
        # 计算总词数
        words = re.findall(r'\w+', all_text.lower())
        total_words = len(words)
        
        # 计算关键词密度
        word_counts = Counter(words)
        keyword_densities = {}
        
        for word, count in word_counts.most_common(20):
            if word not in self.stop_words and len(word) > 2:
                density = (count / total_words) * 100
                keyword_densities[word] = {
                    'count': count,
                    'density': round(density, 2),
                    'is_optimal': 1.0 <= density <= 3.0  # 理想密度范围
                }
        
        return {
            'total_words': total_words,
            'keyword_densities': keyword_densities,
            'density_analysis': self._analyze_density_distribution(keyword_densities)
        }
    
    def _analyze_density_distribution(self, densities: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """分析关键词密度分布"""
        if not densities:
            return {'status': 'no_keywords', 'recommendations': []}
        
        over_optimized = [kw for kw, data in densities.items() if data['density'] > 3.0]
        under_optimized = [kw for kw, data in densities.items() if data['density'] < 1.0]
        optimal = [kw for kw, data in densities.items() if data['is_optimal']]
        
        recommendations = []
        if over_optimized:
            recommendations.append({
                'type': 'reduce_density',
                'keywords': over_optimized[:5],
                'message': '这些关键词密度过高，可能被视为关键词堆砌'
            })
        
        if under_optimized:
            recommendations.append({
                'type': 'increase_density',
                'keywords': under_optimized[:5],
                'message': '这些关键词密度过低，可以适当增加使用频率'
            })
        
        return {
            'status': 'analyzed',
            'optimal_keywords': len(optimal),
            'over_optimized': len(over_optimized),
            'under_optimized': len(under_optimized),
            'recommendations': recommendations
        }
    
    async def _identify_semantic_keywords(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别语义相关关键词"""
        if not self.openai_service or not self.openai_service.is_available():
            return []
        
        # 提取主要内容
        content = ' '.join([
            crawl_data.get('title', ''),
            crawl_data.get('meta_description', ''),
            ' '.join([' '.join(texts) for texts in crawl_data.get('headings', {}).values()])
        ])
        
        if not content:
            return []
        
        prompt = f"""
        基于以下网站内容，生成10-15个语义相关的关键词，这些关键词应该：
        1. 与主要内容主题相关
        2. 包含同义词和相关概念
        3. 适合SEO优化
        4. 包含长尾关键词
        
        网站内容：
        {content[:1000]}
        
        请以JSON格式返回：
        {{
            "semantic_keywords": [
                {{
                    "keyword": "关键词",
                    "relevance": "high/medium/low",
                    "type": "synonym/related/longtail",
                    "search_intent": "informational/commercial/navigational"
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
            return result.get('semantic_keywords', [])
            
        except Exception as e:
            logger.error(f"Semantic keyword identification failed: {str(e)}")
            return []
    
    async def _analyze_competitor_keywords(self, target_url: str, locale: str) -> Dict[str, Any]:
        """分析竞争对手关键词"""
        if not self.serp_api or not self.serp_api.is_available():
            return {'competitors': [], 'analysis': {}}
        
        # 从目标网站提取主要关键词作为搜索词
        # 这里简化处理，实际应该从之前的分析结果中获取
        search_keywords = ["SEO优化", "网站分析", "搜索引擎优化"]  # 示例关键词
        
        competitor_data = {}
        
        try:
            # 分析每个关键词的竞争对手
            for keyword in search_keywords[:3]:  # 限制分析数量
                competitor_analysis = await self.serp_api.competitor_analysis([keyword], locale)
                
                if competitor_analysis and 'top_competitors' in competitor_analysis:
                    for competitor in competitor_analysis['top_competitors'][:3]:
                        domain = competitor['domain']
                        if domain not in competitor_data:
                            competitor_data[domain] = {
                                'domain': domain,
                                'keywords': [],
                                'total_appearances': 0,
                                'avg_position': 0
                            }
                        
                        competitor_data[domain]['keywords'].extend(competitor['keywords'])
                        competitor_data[domain]['total_appearances'] += competitor['total_appearances']
                
                # 添加延迟避免API限制
                await asyncio.sleep(1)
            
            # 计算平均排名
            for domain_data in competitor_data.values():
                if domain_data['keywords']:
                    positions = [kw['position'] for kw in domain_data['keywords']]
                    domain_data['avg_position'] = sum(positions) / len(positions)
            
            # 排序竞争对手
            sorted_competitors = sorted(
                competitor_data.values(),
                key=lambda x: x['total_appearances'],
                reverse=True
            )
            
            return {
                'competitors': sorted_competitors[:self.keyword_config['competitor_analysis_limit']],
                'analysis': {
                    'total_competitors': len(competitor_data),
                    'analyzed_keywords': len(search_keywords),
                    'competitive_landscape': self._assess_competitive_landscape(sorted_competitors)
                }
            }
            
        except Exception as e:
            logger.error(f"Competitor keyword analysis failed: {str(e)}")
            return {'competitors': [], 'analysis': {}}
    
    def _assess_competitive_landscape(self, competitors: List[Dict[str, Any]]) -> str:
        """评估竞争环境"""
        if not competitors:
            return 'low'
        
        # 基于竞争对手数量和活跃度评估
        total_competitors = len(competitors)
        avg_appearances = sum(comp['total_appearances'] for comp in competitors) / total_competitors
        
        if total_competitors > 10 and avg_appearances > 5:
            return 'high'
        elif total_competitors > 5 and avg_appearances > 3:
            return 'medium'
        else:
            return 'low'
    
    async def _discover_keyword_opportunities(self, crawl_data: Dict[str, Any], locale: str) -> List[Dict[str, Any]]:
        """发现关键词机会"""
        opportunities = []
        
        # 基于内容主题发现机会
        content_opportunities = await self._find_content_based_opportunities(crawl_data)
        opportunities.extend(content_opportunities)
        
        # 基于竞争分析发现机会
        if self.serp_api and self.serp_api.is_available():
            competitive_opportunities = await self._find_competitive_opportunities(crawl_data, locale)
            opportunities.extend(competitive_opportunities)
        
        # 基于语义分析发现机会
        if self.openai_service and self.openai_service.is_available():
            semantic_opportunities = await self._find_semantic_opportunities(crawl_data)
            opportunities.extend(semantic_opportunities)
        
        # 去重并排序
        unique_opportunities = {}
        for opp in opportunities:
            key = opp['keyword'].lower()
            if key not in unique_opportunities or opp['opportunity_score'] > unique_opportunities[key]['opportunity_score']:
                unique_opportunities[key] = opp
        
        sorted_opportunities = sorted(
            unique_opportunities.values(),
            key=lambda x: x['opportunity_score'],
            reverse=True
        )
        
        return sorted_opportunities[:20]  # 返回前20个机会
    
    async def _find_content_based_opportunities(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于内容发现关键词机会"""
        opportunities = []
        
        # 分析标题和描述中的关键词扩展机会
        title = crawl_data.get('title', '')
        description = crawl_data.get('meta_description', '')
        
        if title:
            # 生成标题相关的长尾关键词
            title_words = re.findall(r'\w+', title.lower())
            for word in title_words:
                if word not in self.stop_words and len(word) > 3:
                    # 生成相关的长尾关键词
                    longtail_keywords = [
                        f"{word} 教程",
                        f"{word} 方法",
                        f"{word} 技巧",
                        f"如何 {word}",
                        f"{word} 指南"
                    ]
                    
                    for longtail in longtail_keywords:
                        opportunities.append({
                            'keyword': longtail,
                            'opportunity_score': 70,
                            'difficulty': 'medium',
                            'source': 'content_expansion',
                            'reasoning': f'基于标题关键词 "{word}" 的长尾扩展'
                        })
        
        return opportunities[:10]  # 限制数量
    
    async def _find_competitive_opportunities(self, crawl_data: Dict[str, Any], locale: str) -> List[Dict[str, Any]]:
        """基于竞争分析发现机会"""
        # 这里需要实际的竞争对手关键词数据
        # 简化实现，返回一些示例机会
        return [
            {
                'keyword': '本地SEO优化',
                'opportunity_score': 85,
                'difficulty': 'medium',
                'source': 'competitor_gap',
                'reasoning': '竞争对手较少覆盖此关键词'
            },
            {
                'keyword': '移动端SEO',
                'opportunity_score': 80,
                'difficulty': 'medium',
                'source': 'competitor_gap',
                'reasoning': '移动优化相关关键词竞争较小'
            }
        ]
    
    async def _find_semantic_opportunities(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于语义分析发现机会"""
        if not self.openai_service:
            return []
        
        # 使用AI发现语义相关的关键词机会
        content = crawl_data.get('title', '') + ' ' + crawl_data.get('meta_description', '')
        
        prompt = f"""
        基于以下内容，发现5个关键词机会，这些关键词应该：
        1. 与内容相关但当前可能未充分优化
        2. 具有商业价值
        3. 竞争相对较小
        
        内容：{content[:500]}
        
        请以JSON格式返回：
        {{
            "opportunities": [
                {{
                    "keyword": "关键词",
                    "opportunity_score": 1-100,
                    "difficulty": "easy/medium/hard",
                    "reasoning": "发现此机会的原因"
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
            opportunities = result.get('opportunities', [])
            
            # 添加来源标识
            for opp in opportunities:
                opp['source'] = 'semantic_analysis'
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Semantic opportunity discovery failed: {str(e)}")
            return []
    
    async def _identify_keyword_gaps(self, keyword_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别关键词缺口"""
        gaps = []
        
        current_keywords = set(kw['keyword'].lower() for kw in keyword_data['current_keywords'])
        competitor_keywords = set()
        
        # 收集竞争对手关键词
        for competitor in keyword_data.get('competitor_keywords', {}).get('competitors', []):
            for kw_data in competitor.get('keywords', []):
                competitor_keywords.add(kw_data['keyword'].lower())
        
        # 找出竞争对手有但我们没有的关键词
        missing_keywords = competitor_keywords - current_keywords
        
        for keyword in list(missing_keywords)[:15]:  # 限制数量
            gaps.append({
                'keyword': keyword,
                'gap_type': 'competitor_coverage',
                'priority': 'medium',
                'potential_impact': 'medium',
                'recommendation': f'考虑在内容中加入关键词 "{keyword}"'
            })
        
        # 基于语义关键词识别缺口
        semantic_keywords = keyword_data.get('semantic_keywords', [])
        for sem_kw in semantic_keywords:
            if sem_kw['keyword'].lower() not in current_keywords:
                gaps.append({
                    'keyword': sem_kw['keyword'],
                    'gap_type': 'semantic_coverage',
                    'priority': 'high' if sem_kw.get('relevance') == 'high' else 'medium',
                    'potential_impact': sem_kw.get('relevance', 'medium'),
                    'recommendation': f'添加语义相关关键词 "{sem_kw["keyword"]}" 提升内容相关性'
                })
        
        return gaps
    
    async def _generate_keyword_strategy(self, keyword_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成关键词策略"""
        strategy = {
            'primary_keywords': [],
            'secondary_keywords': [],
            'longtail_keywords': [],
            'content_gaps': [],
            'optimization_priorities': []
        }
        
        current_keywords = keyword_data['current_keywords']
        
        # 分类关键词
        for kw in current_keywords[:20]:
            if kw['frequency'] >= 3 and kw['type'] in ['single_word', 'phrase']:
                strategy['primary_keywords'].append(kw)
            elif kw['frequency'] >= 2:
                strategy['secondary_keywords'].append(kw)
            elif len(kw['keyword'].split()) >= 3:
                strategy['longtail_keywords'].append(kw)
        
        # 识别内容缺口
        keyword_opportunities = keyword_data.get('keyword_opportunities', [])
        for opp in keyword_opportunities[:10]:
            if opp['opportunity_score'] >= 70:
                strategy['content_gaps'].append({
                    'keyword': opp['keyword'],
                    'opportunity': opp['opportunity_score'],
                    'difficulty': opp['difficulty'],
                    'action': '创建针对此关键词的内容'
                })
        
        # 生成优化优先级
        strategy['optimization_priorities'] = [
            {
                'priority': 1,
                'action': '优化主要关键词密度',
                'keywords': [kw['keyword'] for kw in strategy['primary_keywords'][:5]],
                'impact': 'high'
            },
            {
                'priority': 2,
                'action': '扩展长尾关键词内容',
                'keywords': [kw['keyword'] for kw in strategy['longtail_keywords'][:5]],
                'impact': 'medium'
            },
            {
                'priority': 3,
                'action': '填补关键词缺口',
                'keywords': [gap['keyword'] for gap in strategy['content_gaps'][:5]],
                'impact': 'high'
            }
        ]
        
        return strategy
    
    async def _prioritize_keywords(self, keyword_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估关键词优先级"""
        all_keywords = []
        
        # 收集所有关键词
        for kw in keyword_data['current_keywords']:
            all_keywords.append({
                'keyword': kw['keyword'],
                'source': 'current',
                'frequency': kw['frequency'],
                'priority_score': kw['frequency'] * 10  # 基础分数
            })
        
        for opp in keyword_data.get('keyword_opportunities', []):
            all_keywords.append({
                'keyword': opp['keyword'],
                'source': 'opportunity',
                'opportunity_score': opp['opportunity_score'],
                'difficulty': opp['difficulty'],
                'priority_score': opp['opportunity_score']
            })
        
        # 按优先级分数排序
        all_keywords.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return all_keywords[:25]  # 返回前25个优先关键词
    
    def _estimate_tokens_used(self, keyword_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 基于分析的关键词数量估算
        total_keywords = len(keyword_data.get('current_keywords', []))
        return total_keywords * 20 + 1000  # 基础token + 关键词处理
    
    def _estimate_cost(self, keyword_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(keyword_data)
        # OpenAI + SERP API 成本
        openai_cost = tokens / 1000 * 0.03
        serp_cost = 0.01  # 假设的SERP API成本
        return openai_cost + serp_cost
