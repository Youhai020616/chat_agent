"""
Link Agent - 链接建设和外链分析

功能：
1. 内部链接结构分析
2. 外部链接质量评估
3. 链接建设机会识别
4. 锚文本优化分析
5. 链接权重分布分析
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter
from urllib.parse import urlparse, urljoin

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class LinkAgent(BaseAgent):
    """链接建设和外链分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("link", config)
        self.openai_service = OpenAIService(config)
        
        # 链接分析维度
        self.link_dimensions = {
            'internal_structure': {'weight': 0.25, 'max_score': 100},
            'external_quality': {'weight': 0.25, 'max_score': 100},
            'anchor_optimization': {'weight': 0.20, 'max_score': 100},
            'link_diversity': {'weight': 0.15, 'max_score': 100},
            'link_velocity': {'weight': 0.15, 'max_score': 100}
        }
        
        # 链接类型
        self.link_types = {
            'internal': '内部链接',
            'external_outbound': '外部出站链接',
            'external_inbound': '外部入站链接'
        }
        
        # 高质量域名指标
        self.quality_indicators = {
            'domain_extensions': ['.edu', '.gov', '.org'],
            'authority_domains': ['wikipedia.org', 'baidu.com', 'zhihu.com'],
            'spam_indicators': ['bit.ly', 'tinyurl.com', 'goo.gl']
        }
        
        # 锚文本类型
        self.anchor_types = {
            'exact_match': '精确匹配',
            'partial_match': '部分匹配',
            'branded': '品牌词',
            'generic': '通用词',
            'naked_url': '裸链接',
            'image': '图片链接'
        }
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行链接建设和外链分析"""
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
            
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行链接分析任务
            tasks = [
                self._analyze_internal_links(crawl_data, state.target_url),
                self._analyze_external_links(crawl_data, state.target_url),
                self._analyze_anchor_text(crawl_data, keyword_insights),
                self._analyze_link_diversity(crawl_data),
                self._identify_link_opportunities(crawl_data, keyword_insights),
                self._analyze_link_quality(crawl_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            link_data = {
                'internal_links_analysis': results[0] if not isinstance(results[0], Exception) else {},
                'external_links_analysis': results[1] if not isinstance(results[1], Exception) else {},
                'anchor_text_analysis': results[2] if not isinstance(results[2], Exception) else {},
                'link_diversity_analysis': results[3] if not isinstance(results[3], Exception) else {},
                'link_opportunities': results[4] if not isinstance(results[4], Exception) else [],
                'link_quality_analysis': results[5] if not isinstance(results[5], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算链接优化总分
            link_data['link_optimization_score'] = await self._calculate_link_score(link_data)
            
            # 生成链接建设策略
            link_data['link_building_strategy'] = await self._generate_link_building_strategy(link_data, keyword_insights)
            
            # 生成链接优化建议
            link_data['recommendations'] = await self._generate_link_recommendations(link_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=link_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(link_data),
                cost=self._estimate_cost(link_data)
            )
            
        except Exception as e:
            logger.error(f"Link analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_internal_links(self, crawl_data: Dict[str, Any], target_url: str) -> Dict[str, Any]:
        """分析内部链接结构"""
        internal_analysis = {
            'total_internal_links': 0,
            'unique_internal_links': 0,
            'internal_link_distribution': {},
            'orphan_pages_risk': 'low',
            'internal_link_score': 0,
            'issues': []
        }
        
        links = crawl_data.get('links', [])
        target_domain = urlparse(target_url).netloc
        
        internal_links = []
        for link in links:
            href = link.get('href', '')
            if href:
                # 处理相对链接
                if href.startswith('/') or href.startswith('#'):
                    internal_links.append(link)
                elif href.startswith('http'):
                    link_domain = urlparse(href).netloc
                    if link_domain == target_domain:
                        internal_links.append(link)
        
        internal_analysis['total_internal_links'] = len(internal_links)
        internal_analysis['unique_internal_links'] = len(set(link.get('href', '') for link in internal_links))
        
        # 分析内部链接分布
        link_targets = [link.get('href', '') for link in internal_links]
        link_distribution = Counter(link_targets)
        internal_analysis['internal_link_distribution'] = dict(link_distribution.most_common(10))
        
        # 评估内部链接结构
        score = 50  # 基础分数
        
        if internal_analysis['total_internal_links'] >= 5:
            score += 25
        elif internal_analysis['total_internal_links'] >= 2:
            score += 15
        else:
            internal_analysis['issues'].append({
                'type': 'insufficient_internal_links',
                'severity': 'medium',
                'message': f'内部链接数量{internal_analysis["total_internal_links"]}过少，建议增加相关页面链接'
            })
        
        # 检查链接文本质量
        empty_text_links = len([link for link in internal_links if not link.get('text', '').strip()])
        if empty_text_links > 0:
            score -= 15
            internal_analysis['issues'].append({
                'type': 'empty_anchor_text',
                'severity': 'medium',
                'message': f'{empty_text_links}个内部链接缺少锚文本'
            })
        
        # 检查链接多样性
        unique_ratio = internal_analysis['unique_internal_links'] / internal_analysis['total_internal_links'] if internal_analysis['total_internal_links'] > 0 else 0
        if unique_ratio < 0.7:
            score -= 10
            internal_analysis['issues'].append({
                'type': 'low_link_diversity',
                'severity': 'low',
                'message': f'内部链接多样性{unique_ratio:.1%}较低，存在重复链接'
            })
        
        internal_analysis['internal_link_score'] = max(0, score)
        
        return internal_analysis
    
    async def _analyze_external_links(self, crawl_data: Dict[str, Any], target_url: str) -> Dict[str, Any]:
        """分析外部链接"""
        external_analysis = {
            'total_external_links': 0,
            'outbound_links': [],
            'external_domains': [],
            'external_link_quality': 0,
            'nofollow_ratio': 0,
            'issues': []
        }
        
        links = crawl_data.get('links', [])
        target_domain = urlparse(target_url).netloc
        
        external_links = []
        for link in links:
            href = link.get('href', '')
            if href and href.startswith('http'):
                link_domain = urlparse(href).netloc
                if link_domain != target_domain:
                    external_links.append(link)
        
        external_analysis['total_external_links'] = len(external_links)
        external_analysis['outbound_links'] = external_links[:10]  # 只保留前10个用于展示
        
        # 分析外部域名
        external_domains = list(set(urlparse(link.get('href', '')).netloc for link in external_links))
        external_analysis['external_domains'] = external_domains
        
        # 评估外部链接质量
        quality_score = 0
        spam_links = 0
        
        for link in external_links:
            href = link.get('href', '')
            domain = urlparse(href).netloc
            
            # 检查高质量域名
            if any(ext in domain for ext in self.quality_indicators['domain_extensions']):
                quality_score += 10
            elif any(auth_domain in domain for auth_domain in self.quality_indicators['authority_domains']):
                quality_score += 5
            
            # 检查垃圾链接
            if any(spam in href for spam in self.quality_indicators['spam_indicators']):
                spam_links += 1
        
        if external_links:
            external_analysis['external_link_quality'] = min(100, quality_score / len(external_links) * 10)
        
        # 检查nofollow比例（简化处理）
        nofollow_links = len([link for link in external_links if 'nofollow' in link.get('rel', '')])
        external_analysis['nofollow_ratio'] = nofollow_links / len(external_links) if external_links else 0
        
        # 识别问题
        if spam_links > 0:
            external_analysis['issues'].append({
                'type': 'spam_links',
                'severity': 'high',
                'message': f'发现{spam_links}个可能的垃圾链接，建议检查和清理'
            })
        
        if external_analysis['nofollow_ratio'] < 0.3 and len(external_links) > 5:
            external_analysis['issues'].append({
                'type': 'low_nofollow_ratio',
                'severity': 'medium',
                'message': f'nofollow链接比例{external_analysis["nofollow_ratio"]:.1%}较低，建议适当增加'
            })
        
        return external_analysis
    
    async def _analyze_anchor_text(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析锚文本优化"""
        anchor_analysis = {
            'anchor_text_distribution': {},
            'anchor_types_distribution': {},
            'keyword_anchor_usage': {},
            'anchor_optimization_score': 0,
            'issues': []
        }
        
        links = crawl_data.get('links', [])
        
        # 收集所有锚文本
        anchor_texts = [link.get('text', '').strip() for link in links if link.get('text', '').strip()]
        anchor_distribution = Counter(anchor_texts)
        anchor_analysis['anchor_text_distribution'] = dict(anchor_distribution.most_common(10))
        
        # 分类锚文本类型
        anchor_types = {
            'exact_match': 0,
            'partial_match': 0,
            'branded': 0,
            'generic': 0,
            'naked_url': 0,
            'image': 0
        }
        
        # 获取主要关键词
        primary_keywords = []
        if keyword_insights:
            current_keywords = keyword_insights.get('current_keywords', [])
            primary_keywords = [kw['keyword'].lower() for kw in current_keywords[:5]]
        
        for anchor_text in anchor_texts:
            anchor_lower = anchor_text.lower()
            
            # 分类锚文本
            if any(keyword in anchor_lower for keyword in primary_keywords):
                if anchor_lower in primary_keywords:
                    anchor_types['exact_match'] += 1
                else:
                    anchor_types['partial_match'] += 1
            elif re.match(r'https?://', anchor_text):
                anchor_types['naked_url'] += 1
            elif anchor_text in ['点击这里', '更多', '阅读更多', 'click here', 'read more']:
                anchor_types['generic'] += 1
            elif '图片' in anchor_text or 'image' in anchor_lower:
                anchor_types['image'] += 1
            else:
                anchor_types['branded'] += 1
        
        total_anchors = sum(anchor_types.values())
        if total_anchors > 0:
            anchor_analysis['anchor_types_distribution'] = {
                k: {'count': v, 'percentage': v / total_anchors * 100}
                for k, v in anchor_types.items()
            }
        
        # 评估锚文本优化分数
        score = 50  # 基础分数
        
        if total_anchors > 0:
            # 检查关键词锚文本比例
            keyword_anchor_ratio = (anchor_types['exact_match'] + anchor_types['partial_match']) / total_anchors
            if 0.1 <= keyword_anchor_ratio <= 0.3:  # 理想比例10-30%
                score += 25
            elif keyword_anchor_ratio > 0.5:
                score -= 20
                anchor_analysis['issues'].append({
                    'type': 'over_optimized_anchors',
                    'severity': 'high',
                    'message': f'关键词锚文本比例{keyword_anchor_ratio:.1%}过高，可能被视为过度优化'
                })
            
            # 检查通用锚文本比例
            generic_ratio = anchor_types['generic'] / total_anchors
            if generic_ratio > 0.3:
                score -= 15
                anchor_analysis['issues'].append({
                    'type': 'too_many_generic_anchors',
                    'severity': 'medium',
                    'message': f'通用锚文本比例{generic_ratio:.1%}过高，建议使用更具描述性的锚文本'
                })
            
            # 检查锚文本多样性
            unique_anchors = len(set(anchor_texts))
            diversity_ratio = unique_anchors / total_anchors
            if diversity_ratio < 0.7:
                score -= 10
                anchor_analysis['issues'].append({
                    'type': 'low_anchor_diversity',
                    'severity': 'low',
                    'message': f'锚文本多样性{diversity_ratio:.1%}较低，建议增加锚文本变化'
                })
        
        anchor_analysis['anchor_optimization_score'] = max(0, score)
        
        return anchor_analysis
    
    async def _analyze_link_diversity(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析链接多样性"""
        diversity_analysis = {
            'domain_diversity': 0,
            'link_type_diversity': 0,
            'anchor_diversity': 0,
            'overall_diversity_score': 0
        }
        
        links = crawl_data.get('links', [])
        
        if not links:
            return diversity_analysis
        
        # 域名多样性
        domains = [urlparse(link.get('href', '')).netloc for link in links if link.get('href', '').startswith('http')]
        unique_domains = len(set(domains))
        total_external_links = len(domains)
        diversity_analysis['domain_diversity'] = unique_domains / total_external_links if total_external_links > 0 else 0
        
        # 链接类型多样性
        link_types = []
        for link in links:
            href = link.get('href', '')
            if href.startswith('#'):
                link_types.append('anchor')
            elif href.startswith('/'):
                link_types.append('internal')
            elif href.startswith('http'):
                link_types.append('external')
            elif href.startswith('mailto:'):
                link_types.append('email')
            elif href.startswith('tel:'):
                link_types.append('phone')
        
        unique_link_types = len(set(link_types))
        diversity_analysis['link_type_diversity'] = unique_link_types / 5  # 最多5种类型
        
        # 锚文本多样性
        anchor_texts = [link.get('text', '').strip() for link in links if link.get('text', '').strip()]
        unique_anchors = len(set(anchor_texts))
        total_anchors = len(anchor_texts)
        diversity_analysis['anchor_diversity'] = unique_anchors / total_anchors if total_anchors > 0 else 0
        
        # 计算总体多样性分数
        diversity_score = (
            diversity_analysis['domain_diversity'] * 0.4 +
            diversity_analysis['link_type_diversity'] * 0.3 +
            diversity_analysis['anchor_diversity'] * 0.3
        ) * 100
        
        diversity_analysis['overall_diversity_score'] = int(diversity_score)
        
        return diversity_analysis
    
    async def _identify_link_opportunities(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别链接建设机会"""
        opportunities = []
        
        # 内部链接机会
        internal_links = crawl_data.get('links', [])
        if len(internal_links) < 5:
            opportunities.append({
                'type': 'internal_linking',
                'priority': 'high',
                'title': '增加内部链接',
                'description': '当前内部链接数量不足，建议增加相关页面之间的链接',
                'potential_impact': 'medium',
                'effort_required': 'low'
            })
        
        # 基于关键词的链接机会
        if keyword_insights:
            keyword_gaps = keyword_insights.get('keyword_gaps', [])
            if keyword_gaps:
                opportunities.append({
                    'type': 'keyword_based_linking',
                    'priority': 'medium',
                    'title': '关键词相关链接建设',
                    'description': f'基于{len(keyword_gaps)}个关键词缺口，寻找相关权威网站建立链接',
                    'potential_impact': 'high',
                    'effort_required': 'high'
                })
        
        # 竞争对手链接机会
        opportunities.append({
            'type': 'competitor_analysis',
            'priority': 'medium',
            'title': '竞争对手链接分析',
            'description': '分析竞争对手的外链策略，寻找类似的链接建设机会',
            'potential_impact': 'high',
            'effort_required': 'medium'
        })
        
        # 内容营销链接机会
        opportunities.append({
            'type': 'content_marketing',
            'priority': 'low',
            'title': '内容营销链接建设',
            'description': '创建高质量内容吸引自然外链，如行业报告、案例研究等',
            'potential_impact': 'high',
            'effort_required': 'high'
        })
        
        return opportunities
    
    async def _analyze_link_quality(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析链接质量"""
        quality_analysis = {
            'overall_quality_score': 0,
            'high_quality_links': 0,
            'medium_quality_links': 0,
            'low_quality_links': 0,
            'quality_distribution': {},
            'quality_issues': []
        }
        
        links = crawl_data.get('links', [])
        external_links = [link for link in links if link.get('href', '').startswith('http')]
        
        if not external_links:
            return quality_analysis
        
        high_quality = 0
        medium_quality = 0
        low_quality = 0
        
        for link in external_links:
            href = link.get('href', '')
            domain = urlparse(href).netloc
            anchor_text = link.get('text', '').strip()
            
            quality_score = 50  # 基础分数
            
            # 域名质量评估
            if any(ext in domain for ext in self.quality_indicators['domain_extensions']):
                quality_score += 30
            elif any(auth_domain in domain for auth_domain in self.quality_indicators['authority_domains']):
                quality_score += 20
            
            # 锚文本质量评估
            if anchor_text and len(anchor_text) > 3:
                quality_score += 10
            
            # 垃圾链接检测
            if any(spam in href for spam in self.quality_indicators['spam_indicators']):
                quality_score -= 40
            
            # 分类链接质量
            if quality_score >= 80:
                high_quality += 1
            elif quality_score >= 60:
                medium_quality += 1
            else:
                low_quality += 1
        
        quality_analysis['high_quality_links'] = high_quality
        quality_analysis['medium_quality_links'] = medium_quality
        quality_analysis['low_quality_links'] = low_quality
        
        # 计算总体质量分数
        total_links = len(external_links)
        if total_links > 0:
            quality_score = (high_quality * 100 + medium_quality * 60 + low_quality * 20) / total_links
            quality_analysis['overall_quality_score'] = int(quality_score)
            
            quality_analysis['quality_distribution'] = {
                'high_quality': high_quality / total_links * 100,
                'medium_quality': medium_quality / total_links * 100,
                'low_quality': low_quality / total_links * 100
            }
        
        # 识别质量问题
        if low_quality > total_links * 0.3:
            quality_analysis['quality_issues'].append({
                'type': 'too_many_low_quality',
                'severity': 'high',
                'message': f'{low_quality}个低质量链接占比{low_quality/total_links:.1%}，建议清理'
            })
        
        return quality_analysis
    
    async def _calculate_link_score(self, link_data: Dict[str, Any]) -> int:
        """计算链接优化总分"""
        total_score = 0
        
        for dimension, config in self.link_dimensions.items():
            dimension_score = 0
            
            if dimension == 'internal_structure':
                internal_analysis = link_data.get('internal_links_analysis', {})
                dimension_score = internal_analysis.get('internal_link_score', 0)
            
            elif dimension == 'external_quality':
                quality_analysis = link_data.get('link_quality_analysis', {})
                dimension_score = quality_analysis.get('overall_quality_score', 0)
            
            elif dimension == 'anchor_optimization':
                anchor_analysis = link_data.get('anchor_text_analysis', {})
                dimension_score = anchor_analysis.get('anchor_optimization_score', 0)
            
            elif dimension == 'link_diversity':
                diversity_analysis = link_data.get('link_diversity_analysis', {})
                dimension_score = diversity_analysis.get('overall_diversity_score', 0)
            
            elif dimension == 'link_velocity':
                # 简化处理，实际需要历史数据
                dimension_score = 70
            
            # 加权计算
            weighted_score = dimension_score * config['weight']
            total_score += weighted_score
        
        return int(total_score)
    
    async def _generate_link_building_strategy(self, link_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成链接建设策略"""
        strategy = {
            'priority_actions': [],
            'target_domains': [],
            'content_opportunities': [],
            'outreach_strategy': {},
            'timeline': {}
        }
        
        # 基于当前链接状况确定优先行动
        internal_score = link_data.get('internal_links_analysis', {}).get('internal_link_score', 0)
        if internal_score < 70:
            strategy['priority_actions'].append({
                'action': '优化内部链接结构',
                'priority': 'high',
                'description': '增加相关页面之间的内部链接，改善网站结构'
            })
        
        quality_score = link_data.get('link_quality_analysis', {}).get('overall_quality_score', 0)
        if quality_score < 60:
            strategy['priority_actions'].append({
                'action': '提升外链质量',
                'priority': 'high',
                'description': '清理低质量链接，寻找高权威域名建立链接'
            })
        
        # 目标域名建议
        strategy['target_domains'] = [
            {'domain': '行业权威网站', 'priority': 'high', 'type': 'authority'},
            {'domain': '相关博客和媒体', 'priority': 'medium', 'type': 'content'},
            {'domain': '合作伙伴网站', 'priority': 'medium', 'type': 'partnership'},
            {'domain': '目录和列表网站', 'priority': 'low', 'type': 'directory'}
        ]
        
        # 内容机会
        strategy['content_opportunities'] = [
            '行业深度报告',
            '案例研究',
            '工具和资源',
            '专家访谈',
            '数据可视化'
        ]
        
        return strategy
    
    async def _generate_link_recommendations(self, link_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成链接优化建议"""
        recommendations = []
        
        # 基于内部链接分析生成建议
        internal_analysis = link_data.get('internal_links_analysis', {})
        for issue in internal_analysis.get('issues', []):
            recommendations.append({
                'category': 'internal_links',
                'priority': issue.get('severity', 'medium'),
                'title': '优化内部链接',
                'description': issue.get('message', ''),
                'impact': 3,
                'effort': 2
            })
        
        # 基于外部链接分析生成建议
        external_analysis = link_data.get('external_links_analysis', {})
        for issue in external_analysis.get('issues', []):
            recommendations.append({
                'category': 'external_links',
                'priority': issue.get('severity', 'medium'),
                'title': '优化外部链接',
                'description': issue.get('message', ''),
                'impact': 4,
                'effort': 3
            })
        
        # 基于锚文本分析生成建议
        anchor_analysis = link_data.get('anchor_text_analysis', {})
        for issue in anchor_analysis.get('issues', []):
            recommendations.append({
                'category': 'anchor_text',
                'priority': issue.get('severity', 'medium'),
                'title': '优化锚文本',
                'description': issue.get('message', ''),
                'impact': 3,
                'effort': 2
            })
        
        return recommendations
    
    def _estimate_tokens_used(self, link_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 链接分析主要基于规则，AI使用较少
        return 200
    
    def _estimate_cost(self, link_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(link_data)
        return tokens / 1000 * 0.03
