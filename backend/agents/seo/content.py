"""
Content Agent - 内容质量和优化分析

功能：
1. 内容质量评估（可读性、结构、深度）
2. 内容SEO优化分析
3. 内容缺口识别
4. 内容策略建议
5. 用户意图匹配分析
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter
import math

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """内容质量和优化分析 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("content", config)
        self.openai_service = OpenAIService(config)
        
        # 内容评估维度
        self.content_dimensions = {
            'readability': {'weight': 0.20, 'max_score': 100},
            'structure': {'weight': 0.20, 'max_score': 100},
            'depth': {'weight': 0.15, 'max_score': 100},
            'seo_optimization': {'weight': 0.20, 'max_score': 100},
            'user_intent': {'weight': 0.15, 'max_score': 100},
            'uniqueness': {'weight': 0.10, 'max_score': 100}
        }
        
        # 内容类型
        self.content_types = [
            'informational',    # 信息型
            'commercial',       # 商业型
            'navigational',     # 导航型
            'transactional'     # 交易型
        ]
        
        # 可读性评估标准
        self.readability_metrics = {
            'avg_sentence_length': {'ideal': 20, 'max': 30},
            'avg_word_length': {'ideal': 5, 'max': 7},
            'paragraph_length': {'ideal': 100, 'max': 150},
            'complex_words_ratio': {'max': 0.15}
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
        """执行内容质量和优化分析"""
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
            
            if not crawl_data:
                return AgentResult(
                    success=False,
                    data={},
                    error="No crawl data available"
                )
            
            # 并行执行内容分析任务
            tasks = [
                self._analyze_content_readability(crawl_data),
                self._analyze_content_structure(crawl_data),
                self._analyze_content_depth(crawl_data),
                self._analyze_seo_optimization(crawl_data, keyword_insights),
                self._analyze_user_intent(crawl_data, keyword_insights),
                self._analyze_content_uniqueness(crawl_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合分析结果
            content_data = {
                'readability_analysis': results[0] if not isinstance(results[0], Exception) else {},
                'structure_analysis': results[1] if not isinstance(results[1], Exception) else {},
                'depth_analysis': results[2] if not isinstance(results[2], Exception) else {},
                'seo_optimization': results[3] if not isinstance(results[3], Exception) else {},
                'user_intent_analysis': results[4] if not isinstance(results[4], Exception) else {},
                'uniqueness_analysis': results[5] if not isinstance(results[5], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 计算内容质量总分
            content_data['content_quality_score'] = await self._calculate_content_score(content_data)
            
            # 识别内容缺口
            content_data['content_gaps'] = await self._identify_content_gaps(content_data, keyword_insights)
            
            # 生成内容优化建议
            content_data['recommendations'] = await self._generate_content_recommendations(content_data)
            
            # 生成内容策略
            content_data['content_strategy'] = await self._generate_content_strategy(content_data, keyword_insights)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=content_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(content_data),
                cost=self._estimate_cost(content_data)
            )
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_content_readability(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容可读性"""
        readability = {
            'readability_score': 0,
            'metrics': {},
            'issues': [],
            'suggestions': []
        }
        
        # 提取主要文本内容
        content_text = self._extract_main_content(crawl_data)
        if not content_text:
            readability['issues'].append({
                'type': 'no_content',
                'severity': 'critical',
                'message': '页面缺少主要文本内容'
            })
            return readability
        
        # 计算可读性指标
        sentences = self._split_sentences(content_text)
        words = self._split_words(content_text)
        paragraphs = content_text.split('\n\n')
        
        # 平均句子长度
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        readability['metrics']['avg_sentence_length'] = avg_sentence_length
        
        # 平均词长
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        readability['metrics']['avg_word_length'] = avg_word_length
        
        # 平均段落长度
        avg_paragraph_length = len(words) / len(paragraphs) if paragraphs else 0
        readability['metrics']['avg_paragraph_length'] = avg_paragraph_length
        
        # 复杂词汇比例
        complex_words = [word for word in words if len(word) > 6 and word not in self.stop_words]
        complex_words_ratio = len(complex_words) / len(words) if words else 0
        readability['metrics']['complex_words_ratio'] = complex_words_ratio
        
        # 评估可读性分数
        score = 100
        
        # 句子长度评估
        if avg_sentence_length > self.readability_metrics['avg_sentence_length']['max']:
            score -= 20
            readability['issues'].append({
                'type': 'long_sentences',
                'severity': 'medium',
                'message': f'平均句子长度{avg_sentence_length:.1f}词过长，建议控制在{self.readability_metrics["avg_sentence_length"]["ideal"]}词以内'
            })
        
        # 词汇复杂度评估
        if complex_words_ratio > self.readability_metrics['complex_words_ratio']['max']:
            score -= 15
            readability['issues'].append({
                'type': 'complex_vocabulary',
                'severity': 'medium',
                'message': f'复杂词汇比例{complex_words_ratio:.1%}过高，建议使用更简单的词汇'
            })
        
        # 段落长度评估
        if avg_paragraph_length > self.readability_metrics['paragraph_length']['max']:
            score -= 15
            readability['issues'].append({
                'type': 'long_paragraphs',
                'severity': 'low',
                'message': f'平均段落长度{avg_paragraph_length:.1f}词过长，建议分解长段落'
            })
        
        readability['readability_score'] = max(0, score)
        
        return readability
    
    async def _analyze_content_structure(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容结构"""
        structure = {
            'structure_score': 0,
            'heading_analysis': {},
            'content_organization': {},
            'issues': [],
            'suggestions': []
        }
        
        # 分析标题结构
        headings = crawl_data.get('headings', {})
        structure['heading_analysis'] = {
            'h1_count': len(headings.get('h1', [])),
            'h2_count': len(headings.get('h2', [])),
            'h3_count': len(headings.get('h3', [])),
            'total_headings': sum(len(texts) for texts in headings.values()),
            'hierarchy_issues': []
        }
        
        # 检查标题层级
        if structure['heading_analysis']['h1_count'] == 0:
            structure['issues'].append({
                'type': 'missing_h1',
                'severity': 'high',
                'message': '页面缺少H1标题'
            })
        elif structure['heading_analysis']['h1_count'] > 1:
            structure['issues'].append({
                'type': 'multiple_h1',
                'severity': 'medium',
                'message': f'页面有{structure["heading_analysis"]["h1_count"]}个H1标题，建议只使用一个'
            })
        
        # 检查内容组织
        content_text = self._extract_main_content(crawl_data)
        if content_text:
            word_count = len(self._split_words(content_text))
            paragraph_count = len(content_text.split('\n\n'))
            
            structure['content_organization'] = {
                'word_count': word_count,
                'paragraph_count': paragraph_count,
                'avg_words_per_paragraph': word_count / paragraph_count if paragraph_count > 0 else 0
            }
            
            # 内容长度评估
            if word_count < 300:
                structure['issues'].append({
                    'type': 'thin_content',
                    'severity': 'high',
                    'message': f'内容长度{word_count}词过短，建议增加到至少300词'
                })
            elif word_count > 3000:
                structure['suggestions'].append({
                    'type': 'long_content',
                    'message': f'内容长度{word_count}词较长，考虑分解为多个页面或添加目录导航'
                })
        
        # 计算结构分数
        score = 100
        score -= len([issue for issue in structure['issues'] if issue['severity'] == 'high']) * 25
        score -= len([issue for issue in structure['issues'] if issue['severity'] == 'medium']) * 15
        
        structure['structure_score'] = max(0, score)
        
        return structure
    
    async def _analyze_content_depth(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容深度"""
        depth = {
            'depth_score': 0,
            'topic_coverage': {},
            'expertise_indicators': [],
            'content_comprehensiveness': 0
        }
        
        content_text = self._extract_main_content(crawl_data)
        if not content_text:
            return depth
        
        # 分析主题覆盖度
        words = self._split_words(content_text)
        word_freq = Counter(word.lower() for word in words if word not in self.stop_words and len(word) > 3)
        
        # 识别主要主题
        main_topics = word_freq.most_common(10)
        depth['topic_coverage'] = {
            'main_topics': [{'topic': topic, 'frequency': freq} for topic, freq in main_topics],
            'topic_diversity': len(set(word for word, _ in main_topics))
        }
        
        # 检查专业性指标
        expertise_keywords = ['专业', '经验', '研究', '分析', '数据', '案例', '实践', '方法', '技术', '解决方案']
        for keyword in expertise_keywords:
            if keyword in content_text:
                depth['expertise_indicators'].append(keyword)
        
        # 计算内容全面性
        unique_words = len(set(word.lower() for word in words if word not in self.stop_words))
        total_words = len([word for word in words if word not in self.stop_words])
        lexical_diversity = unique_words / total_words if total_words > 0 else 0
        
        depth['content_comprehensiveness'] = int(lexical_diversity * 100)
        
        # 计算深度分数
        score = 50  # 基础分数
        
        # 基于词汇多样性加分
        if lexical_diversity > 0.6:
            score += 25
        elif lexical_diversity > 0.4:
            score += 15
        
        # 基于专业性指标加分
        score += min(25, len(depth['expertise_indicators']) * 5)
        
        depth['depth_score'] = min(100, score)
        
        return depth
    
    async def _analyze_seo_optimization(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析SEO优化程度"""
        seo_opt = {
            'seo_score': 0,
            'keyword_optimization': {},
            'meta_optimization': {},
            'content_optimization': {},
            'issues': []
        }
        
        # 分析关键词优化
        if keyword_insights:
            current_keywords = keyword_insights.get('current_keywords', [])
            keyword_density = keyword_insights.get('keyword_density', {})
            
            seo_opt['keyword_optimization'] = {
                'primary_keywords_count': len([kw for kw in current_keywords if kw.get('frequency', 0) >= 3]),
                'keyword_density_optimal': len([kw for kw, data in keyword_density.get('keyword_densities', {}).items() if data.get('is_optimal', False)]),
                'over_optimized_keywords': len([kw for kw, data in keyword_density.get('keyword_densities', {}).items() if data.get('density', 0) > 3.0])
            }
        
        # 分析Meta优化
        title = crawl_data.get('title', '')
        meta_desc = crawl_data.get('meta_description', '')
        
        seo_opt['meta_optimization'] = {
            'title_length': len(title),
            'title_optimal': 30 <= len(title) <= 60,
            'meta_desc_length': len(meta_desc),
            'meta_desc_optimal': 120 <= len(meta_desc) <= 160,
            'has_meta_desc': bool(meta_desc)
        }
        
        # 分析内容优化
        content_text = self._extract_main_content(crawl_data)
        if content_text:
            # 检查关键词在内容中的分布
            keyword_in_first_paragraph = False
            if current_keywords and content_text:
                first_paragraph = content_text.split('\n\n')[0] if '\n\n' in content_text else content_text[:200]
                primary_keyword = current_keywords[0]['keyword'] if current_keywords else ''
                keyword_in_first_paragraph = primary_keyword.lower() in first_paragraph.lower()
            
            seo_opt['content_optimization'] = {
                'content_length': len(self._split_words(content_text)),
                'keyword_in_first_paragraph': keyword_in_first_paragraph,
                'internal_links': len(crawl_data.get('links', [])),
                'images_with_alt': len([img for img in crawl_data.get('images', []) if img.get('alt')])
            }
        
        # 计算SEO优化分数
        score = 0
        
        # Meta标签优化分数 (40%)
        if seo_opt['meta_optimization']['title_optimal']:
            score += 20
        if seo_opt['meta_optimization']['meta_desc_optimal']:
            score += 20
        
        # 关键词优化分数 (40%)
        if keyword_insights:
            if seo_opt['keyword_optimization']['primary_keywords_count'] > 0:
                score += 15
            if seo_opt['keyword_optimization']['keyword_density_optimal'] > 0:
                score += 15
            if seo_opt['keyword_optimization']['over_optimized_keywords'] == 0:
                score += 10
        
        # 内容优化分数 (20%)
        if content_text:
            if seo_opt['content_optimization']['content_length'] >= 300:
                score += 10
            if seo_opt['content_optimization']['keyword_in_first_paragraph']:
                score += 10
        
        seo_opt['seo_score'] = score
        
        return seo_opt
    
    async def _analyze_user_intent(self, crawl_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析用户意图匹配"""
        intent_analysis = {
            'intent_score': 0,
            'detected_intent': 'unknown',
            'intent_signals': [],
            'content_intent_match': 0
        }
        
        content_text = self._extract_main_content(crawl_data)
        title = crawl_data.get('title', '')
        
        # 检测用户意图信号
        informational_signals = ['什么是', '如何', '怎么', '为什么', '指南', '教程', 'what', 'how', 'why', 'guide', 'tutorial']
        commercial_signals = ['最好的', '比较', '评价', '推荐', '选择', 'best', 'compare', 'review', 'recommend']
        transactional_signals = ['购买', '价格', '优惠', '联系', '咨询', 'buy', 'price', 'contact', 'purchase']
        navigational_signals = ['官网', '登录', '注册', '首页', 'official', 'login', 'register', 'home']
        
        all_text = f"{title} {content_text}".lower()
        
        intent_scores = {
            'informational': sum(1 for signal in informational_signals if signal in all_text),
            'commercial': sum(1 for signal in commercial_signals if signal in all_text),
            'transactional': sum(1 for signal in transactional_signals if signal in all_text),
            'navigational': sum(1 for signal in navigational_signals if signal in all_text)
        }
        
        # 确定主要意图
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            intent_analysis['detected_intent'] = primary_intent
            intent_analysis['intent_signals'] = [signal for signal in locals()[f"{primary_intent}_signals"] if signal in all_text]
        
        # 计算意图匹配分数
        max_intent_score = max(intent_scores.values()) if intent_scores.values() else 0
        intent_analysis['intent_score'] = min(100, max_intent_score * 20)
        
        return intent_analysis
    
    async def _analyze_content_uniqueness(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容独特性"""
        uniqueness = {
            'uniqueness_score': 0,
            'duplicate_content_risk': 'low',
            'content_originality': {},
            'suggestions': []
        }
        
        content_text = self._extract_main_content(crawl_data)
        if not content_text:
            return uniqueness
        
        # 简化的原创性分析
        sentences = self._split_sentences(content_text)
        
        # 检查重复句子
        sentence_counts = Counter(sentences)
        duplicate_sentences = [sent for sent, count in sentence_counts.items() if count > 1]
        
        uniqueness['content_originality'] = {
            'total_sentences': len(sentences),
            'unique_sentences': len(set(sentences)),
            'duplicate_sentences': len(duplicate_sentences),
            'uniqueness_ratio': len(set(sentences)) / len(sentences) if sentences else 0
        }
        
        # 评估独特性分数
        uniqueness_ratio = uniqueness['content_originality']['uniqueness_ratio']
        if uniqueness_ratio >= 0.95:
            uniqueness['uniqueness_score'] = 100
            uniqueness['duplicate_content_risk'] = 'low'
        elif uniqueness_ratio >= 0.85:
            uniqueness['uniqueness_score'] = 80
            uniqueness['duplicate_content_risk'] = 'medium'
        else:
            uniqueness['uniqueness_score'] = 60
            uniqueness['duplicate_content_risk'] = 'high'
            uniqueness['suggestions'].append('检查并减少重复内容，提高内容原创性')
        
        return uniqueness
    
    def _extract_main_content(self, crawl_data: Dict[str, Any]) -> str:
        """提取主要内容文本"""
        content_parts = []
        
        # 从标题和描述中提取
        if crawl_data.get('title'):
            content_parts.append(crawl_data['title'])
        
        if crawl_data.get('meta_description'):
            content_parts.append(crawl_data['meta_description'])
        
        # 从标题层级中提取
        headings = crawl_data.get('headings', {})
        for level, texts in headings.items():
            content_parts.extend(texts)
        
        return ' '.join(content_parts)
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 简化的句子分割
        sentences = re.split(r'[。！？.!?]+', text)
        return [sent.strip() for sent in sentences if sent.strip()]
    
    def _split_words(self, text: str) -> List[str]:
        """分割词汇"""
        # 简化的词汇分割
        words = re.findall(r'\w+', text)
        return [word for word in words if len(word) > 1]
    
    async def _calculate_content_score(self, content_data: Dict[str, Any]) -> int:
        """计算内容质量总分"""
        total_score = 0
        
        for dimension, config in self.content_dimensions.items():
            dimension_score = 0
            
            if dimension == 'readability':
                readability = content_data.get('readability_analysis', {})
                dimension_score = readability.get('readability_score', 0)
            
            elif dimension == 'structure':
                structure = content_data.get('structure_analysis', {})
                dimension_score = structure.get('structure_score', 0)
            
            elif dimension == 'depth':
                depth = content_data.get('depth_analysis', {})
                dimension_score = depth.get('depth_score', 0)
            
            elif dimension == 'seo_optimization':
                seo_opt = content_data.get('seo_optimization', {})
                dimension_score = seo_opt.get('seo_score', 0)
            
            elif dimension == 'user_intent':
                intent = content_data.get('user_intent_analysis', {})
                dimension_score = intent.get('intent_score', 0)
            
            elif dimension == 'uniqueness':
                uniqueness = content_data.get('uniqueness_analysis', {})
                dimension_score = uniqueness.get('uniqueness_score', 0)
            
            # 加权计算
            weighted_score = dimension_score * config['weight']
            total_score += weighted_score
        
        return int(total_score)
    
    async def _identify_content_gaps(self, content_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别内容缺口"""
        gaps = []
        
        # 基于结构分析识别缺口
        structure = content_data.get('structure_analysis', {})
        if structure.get('content_organization', {}).get('word_count', 0) < 300:
            gaps.append({
                'gap_type': 'content_length',
                'priority': 'high',
                'description': '内容长度不足，需要增加更多有价值的信息',
                'recommendation': '扩展内容到至少300词，增加详细说明和案例'
            })
        
        # 基于深度分析识别缺口
        depth = content_data.get('depth_analysis', {})
        if len(depth.get('expertise_indicators', [])) < 3:
            gaps.append({
                'gap_type': 'expertise_depth',
                'priority': 'medium',
                'description': '内容缺乏专业性指标',
                'recommendation': '增加专业术语、数据支持、案例研究等专业性内容'
            })
        
        # 基于SEO优化识别缺口
        seo_opt = content_data.get('seo_optimization', {})
        if not seo_opt.get('meta_optimization', {}).get('has_meta_desc'):
            gaps.append({
                'gap_type': 'meta_description',
                'priority': 'high',
                'description': '缺少Meta描述',
                'recommendation': '添加120-160字符的Meta描述，包含主要关键词'
            })
        
        return gaps
    
    async def _generate_content_recommendations(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成内容优化建议"""
        recommendations = []
        
        # 基于可读性分析生成建议
        readability = content_data.get('readability_analysis', {})
        for issue in readability.get('issues', []):
            recommendations.append({
                'category': 'readability',
                'priority': issue.get('severity', 'medium'),
                'title': '改善内容可读性',
                'description': issue.get('message', ''),
                'impact': 3,
                'effort': 2
            })
        
        # 基于结构分析生成建议
        structure = content_data.get('structure_analysis', {})
        for issue in structure.get('issues', []):
            recommendations.append({
                'category': 'structure',
                'priority': issue.get('severity', 'medium'),
                'title': '优化内容结构',
                'description': issue.get('message', ''),
                'impact': 4,
                'effort': 2
            })
        
        # 基于SEO优化生成建议
        seo_opt = content_data.get('seo_optimization', {})
        if seo_opt.get('seo_score', 0) < 70:
            recommendations.append({
                'category': 'seo',
                'priority': 'high',
                'title': '提升SEO优化水平',
                'description': f'当前SEO优化分数{seo_opt.get("seo_score", 0)}分，需要优化关键词使用和Meta标签',
                'impact': 5,
                'effort': 3
            })
        
        return recommendations
    
    async def _generate_content_strategy(self, content_data: Dict[str, Any], keyword_insights: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成内容策略"""
        strategy = {
            'content_pillars': [],
            'content_calendar': {},
            'optimization_priorities': [],
            'content_formats': []
        }
        
        # 基于用户意图确定内容支柱
        intent_analysis = content_data.get('user_intent_analysis', {})
        detected_intent = intent_analysis.get('detected_intent', 'informational')
        
        if detected_intent == 'informational':
            strategy['content_pillars'] = ['教育内容', '指南教程', '行业洞察', '最佳实践']
            strategy['content_formats'] = ['详细指南', '步骤教程', '案例研究', '常见问题']
        elif detected_intent == 'commercial':
            strategy['content_pillars'] = ['产品比较', '用户评价', '选择指南', '功能介绍']
            strategy['content_formats'] = ['比较表格', '评测文章', '用户故事', '产品演示']
        elif detected_intent == 'transactional':
            strategy['content_pillars'] = ['产品信息', '价格方案', '购买指南', '客户支持']
            strategy['content_formats'] = ['产品页面', '定价表', '购买流程', '联系表单']
        
        # 设置优化优先级
        content_score = content_data.get('content_quality_score', 0)
        if content_score < 60:
            strategy['optimization_priorities'] = [
                {'priority': 1, 'action': '提升内容质量', 'focus': '可读性和结构'},
                {'priority': 2, 'action': '增强SEO优化', 'focus': '关键词和Meta标签'},
                {'priority': 3, 'action': '扩展内容深度', 'focus': '专业性和全面性'}
            ]
        elif content_score < 80:
            strategy['optimization_priorities'] = [
                {'priority': 1, 'action': '精细化SEO优化', 'focus': '关键词密度和分布'},
                {'priority': 2, 'action': '提升用户体验', 'focus': '内容结构和导航'},
                {'priority': 3, 'action': '增加互动元素', 'focus': '用户参与度'}
            ]
        
        return strategy
    
    def _estimate_tokens_used(self, content_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 内容分析主要基于规则，AI使用较少
        base_tokens = 300
        if content_data.get('content_strategy', {}).get('content_pillars'):
            base_tokens += 200
        return base_tokens
    
    def _estimate_cost(self, content_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(content_data)
        return tokens / 1000 * 0.03
