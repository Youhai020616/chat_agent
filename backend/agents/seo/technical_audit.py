"""
TechnicalAudit Agent - 技术 SEO 审计

功能：
1. 页面性能分析（加载速度、Core Web Vitals）
2. HTML 结构和标签优化检查
3. 移动端友好性分析
4. 网站架构和 URL 结构分析
5. 索引和爬虫友好性检查
"""

import re
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import json

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class TechnicalAuditAgent(BaseAgent):
    """技术 SEO 审计 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("technical_audit", config)
        self.openai_service = OpenAIService(config)
        
        # 技术 SEO 检查规则
        self.seo_rules = {
            'title_length': {'min': 30, 'max': 60},
            'meta_description_length': {'min': 120, 'max': 160},
            'h1_count': {'min': 1, 'max': 1},
            'image_alt_ratio': {'min': 0.8},  # 80% 的图片应该有 alt 属性
            'internal_link_ratio': {'min': 0.1},  # 至少 10% 的链接应该是内部链接
            'page_speed_threshold': 3.0,  # 页面加载时间阈值（秒）
        }
        
        # Core Web Vitals 阈值
        self.cwv_thresholds = {
            'lcp': {'good': 2.5, 'needs_improvement': 4.0},  # Largest Contentful Paint
            'fid': {'good': 100, 'needs_improvement': 300},  # First Input Delay
            'cls': {'good': 0.1, 'needs_improvement': 0.25}  # Cumulative Layout Shift
        }
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行技术 SEO 审计"""
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
            
            # 并行执行各种技术审计
            tasks = [
                self._analyze_page_performance(crawl_data),
                self._analyze_html_structure(crawl_data),
                self._analyze_meta_tags(crawl_data),
                self._analyze_heading_structure(crawl_data),
                self._analyze_images(crawl_data),
                self._analyze_links(crawl_data, state.target_url),
                self._analyze_mobile_friendliness(crawl_data),
                self._analyze_schema_markup(crawl_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合审计结果
            audit_data = {
                'page_performance': results[0] if not isinstance(results[0], Exception) else {},
                'html_structure': results[1] if not isinstance(results[1], Exception) else {},
                'meta_tags': results[2] if not isinstance(results[2], Exception) else {},
                'heading_structure': results[3] if not isinstance(results[3], Exception) else {},
                'images_analysis': results[4] if not isinstance(results[4], Exception) else {},
                'links_analysis': results[5] if not isinstance(results[5], Exception) else {},
                'mobile_friendliness': results[6] if not isinstance(results[6], Exception) else {},
                'schema_markup': results[7] if not isinstance(results[7], Exception) else {},
                'audit_metadata': {
                    'audited_at': datetime.utcnow().isoformat(),
                    'url': state.target_url,
                    'locale': state.locale,
                    'user_agent': 'SEO-GEO-Bot/1.0'
                }
            }
            
            # 计算总体技术 SEO 分数
            audit_data['overall_score'] = await self._calculate_technical_score(audit_data)
            
            # 生成技术优化建议
            audit_data['recommendations'] = await self._generate_technical_recommendations(audit_data)
            
            # 识别关键问题
            audit_data['critical_issues'] = await self._identify_critical_issues(audit_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=audit_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(crawl_data),
                cost=self._estimate_cost(crawl_data)
            )
            
        except Exception as e:
            logger.error(f"Technical audit failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _analyze_page_performance(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析页面性能"""
        performance = {
            'load_time': crawl_data.get('load_time', 0),
            'content_length': crawl_data.get('content_length', 0),
            'status_code': crawl_data.get('status_code', 0),
            'lighthouse_scores': crawl_data.get('lighthouse_scores', {}),
            'performance_score': 0,
            'issues': []
        }
        
        # 检查加载时间
        load_time = performance['load_time']
        if load_time > self.seo_rules['page_speed_threshold']:
            performance['issues'].append({
                'type': 'slow_loading',
                'severity': 'high',
                'message': f'页面加载时间 {load_time:.2f}s 超过推荐阈值 {self.seo_rules["page_speed_threshold"]}s',
                'recommendation': '优化图片大小、启用压缩、使用 CDN'
            })
        
        # 检查 HTTP 状态码
        if performance['status_code'] != 200:
            performance['issues'].append({
                'type': 'http_error',
                'severity': 'critical',
                'message': f'HTTP 状态码 {performance["status_code"]} 不正常',
                'recommendation': '检查服务器配置和页面可访问性'
            })
        
        # 计算性能分数
        score = 100
        if load_time > 1.0:
            score -= min(50, (load_time - 1.0) * 10)
        if performance['status_code'] != 200:
            score -= 30
        
        performance['performance_score'] = max(0, score)
        
        return performance
    
    async def _analyze_html_structure(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析 HTML 结构"""
        structure = {
            'has_doctype': True,  # 假设现代网站都有 DOCTYPE
            'has_lang_attribute': True,  # 需要从实际 HTML 中检查
            'has_charset': True,  # 需要从实际 HTML 中检查
            'has_viewport': True,  # 需要从实际 HTML 中检查
            'structure_score': 0,
            'issues': []
        }
        
        # 这里可以添加更详细的 HTML 结构分析
        # 由于我们只有爬虫提取的数据，无法完全分析 HTML 结构
        # 在实际实现中，需要保存完整的 HTML 内容进行分析
        
        # 基于可用数据进行基础检查
        title = crawl_data.get('title')
        if not title:
            structure['issues'].append({
                'type': 'missing_title',
                'severity': 'critical',
                'message': '页面缺少 title 标签',
                'recommendation': '添加描述性的页面标题'
            })
        
        meta_description = crawl_data.get('meta_description')
        if not meta_description:
            structure['issues'].append({
                'type': 'missing_meta_description',
                'severity': 'high',
                'message': '页面缺少 meta description',
                'recommendation': '添加 150-160 字符的页面描述'
            })
        
        # 计算结构分数
        score = 100
        score -= len([issue for issue in structure['issues'] if issue['severity'] == 'critical']) * 20
        score -= len([issue for issue in structure['issues'] if issue['severity'] == 'high']) * 10
        
        structure['structure_score'] = max(0, score)
        
        return structure
    
    async def _analyze_meta_tags(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析 Meta 标签"""
        meta_analysis = {
            'title': {
                'content': crawl_data.get('title', ''),
                'length': len(crawl_data.get('title', '')),
                'issues': []
            },
            'description': {
                'content': crawl_data.get('meta_description', ''),
                'length': len(crawl_data.get('meta_description', '')),
                'issues': []
            },
            'keywords': {
                'content': crawl_data.get('meta_keywords', ''),
                'count': len(crawl_data.get('meta_keywords', '').split(',')) if crawl_data.get('meta_keywords') else 0,
                'issues': []
            },
            'meta_score': 0
        }
        
        # 检查 title 标签
        title_length = meta_analysis['title']['length']
        if title_length == 0:
            meta_analysis['title']['issues'].append({
                'type': 'missing_title',
                'severity': 'critical',
                'message': '缺少页面标题'
            })
        elif title_length < self.seo_rules['title_length']['min']:
            meta_analysis['title']['issues'].append({
                'type': 'title_too_short',
                'severity': 'medium',
                'message': f'标题长度 {title_length} 字符过短，建议 {self.seo_rules["title_length"]["min"]}-{self.seo_rules["title_length"]["max"]} 字符'
            })
        elif title_length > self.seo_rules['title_length']['max']:
            meta_analysis['title']['issues'].append({
                'type': 'title_too_long',
                'severity': 'medium',
                'message': f'标题长度 {title_length} 字符过长，建议 {self.seo_rules["title_length"]["min"]}-{self.seo_rules["title_length"]["max"]} 字符'
            })
        
        # 检查 meta description
        desc_length = meta_analysis['description']['length']
        if desc_length == 0:
            meta_analysis['description']['issues'].append({
                'type': 'missing_description',
                'severity': 'high',
                'message': '缺少页面描述'
            })
        elif desc_length < self.seo_rules['meta_description_length']['min']:
            meta_analysis['description']['issues'].append({
                'type': 'description_too_short',
                'severity': 'medium',
                'message': f'描述长度 {desc_length} 字符过短，建议 {self.seo_rules["meta_description_length"]["min"]}-{self.seo_rules["meta_description_length"]["max"]} 字符'
            })
        elif desc_length > self.seo_rules['meta_description_length']['max']:
            meta_analysis['description']['issues'].append({
                'type': 'description_too_long',
                'severity': 'medium',
                'message': f'描述长度 {desc_length} 字符过长，建议 {self.seo_rules["meta_description_length"]["min"]}-{self.seo_rules["meta_description_length"]["max"]} 字符'
            })
        
        # 检查 meta keywords（虽然现在不太重要）
        if meta_analysis['keywords']['count'] > 10:
            meta_analysis['keywords']['issues'].append({
                'type': 'too_many_keywords',
                'severity': 'low',
                'message': f'关键词数量 {meta_analysis["keywords"]["count"]} 过多，建议控制在 5-10 个'
            })
        
        # 计算 meta 标签分数
        score = 100
        for section in ['title', 'description', 'keywords']:
            for issue in meta_analysis[section]['issues']:
                if issue['severity'] == 'critical':
                    score -= 25
                elif issue['severity'] == 'high':
                    score -= 15
                elif issue['severity'] == 'medium':
                    score -= 10
                elif issue['severity'] == 'low':
                    score -= 5
        
        meta_analysis['meta_score'] = max(0, score)
        
        return meta_analysis
    
    async def _analyze_heading_structure(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析标题结构"""
        headings = crawl_data.get('headings', {})
        
        heading_analysis = {
            'structure': headings,
            'h1_count': len(headings.get('h1', [])),
            'total_headings': sum(len(texts) for texts in headings.values()),
            'hierarchy_issues': [],
            'heading_score': 0
        }
        
        # 检查 H1 标签
        h1_count = heading_analysis['h1_count']
        if h1_count == 0:
            heading_analysis['hierarchy_issues'].append({
                'type': 'missing_h1',
                'severity': 'high',
                'message': '页面缺少 H1 标签',
                'recommendation': '添加一个描述页面主题的 H1 标签'
            })
        elif h1_count > 1:
            heading_analysis['hierarchy_issues'].append({
                'type': 'multiple_h1',
                'severity': 'medium',
                'message': f'页面有 {h1_count} 个 H1 标签，建议只使用一个',
                'recommendation': '保留最重要的 H1，其他改为 H2 或更低级别'
            })
        
        # 检查标题层级结构
        heading_levels = []
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if headings.get(level):
                heading_levels.append(int(level[1]))
        
        if heading_levels:
            # 检查是否跳级
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    heading_analysis['hierarchy_issues'].append({
                        'type': 'skipped_heading_level',
                        'severity': 'low',
                        'message': f'标题层级跳跃：从 H{heading_levels[i-1]} 直接到 H{heading_levels[i]}',
                        'recommendation': '保持标题层级的连续性'
                    })
        
        # 计算标题结构分数
        score = 100
        if h1_count == 0:
            score -= 30
        elif h1_count > 1:
            score -= 15
        
        score -= len([issue for issue in heading_analysis['hierarchy_issues'] if issue['severity'] == 'low']) * 5
        
        heading_analysis['heading_score'] = max(0, score)
        
        return heading_analysis
    
    async def _analyze_images(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析图片优化"""
        images = crawl_data.get('images', [])
        
        image_analysis = {
            'total_images': len(images),
            'images_with_alt': 0,
            'images_without_alt': 0,
            'alt_ratio': 0,
            'issues': [],
            'image_score': 0
        }
        
        if images:
            # 统计有 alt 属性的图片
            for img in images:
                if img.get('alt') and img['alt'].strip():
                    image_analysis['images_with_alt'] += 1
                else:
                    image_analysis['images_without_alt'] += 1
            
            # 计算 alt 属性比例
            image_analysis['alt_ratio'] = image_analysis['images_with_alt'] / len(images)
            
            # 检查 alt 属性覆盖率
            if image_analysis['alt_ratio'] < self.seo_rules['image_alt_ratio']:
                image_analysis['issues'].append({
                    'type': 'low_alt_coverage',
                    'severity': 'medium',
                    'message': f'只有 {image_analysis["alt_ratio"]:.1%} 的图片有 alt 属性，建议达到 {self.seo_rules["image_alt_ratio"]:.0%}',
                    'recommendation': '为所有重要图片添加描述性的 alt 属性'
                })
            
            # 检查空的 alt 属性
            empty_alt_count = len([img for img in images if img.get('alt') == ''])
            if empty_alt_count > 0:
                image_analysis['issues'].append({
                    'type': 'empty_alt_attributes',
                    'severity': 'low',
                    'message': f'{empty_alt_count} 个图片的 alt 属性为空',
                    'recommendation': '为装饰性图片使用空 alt=""，为内容图片添加描述'
                })
        
        # 计算图片优化分数
        score = 100
        if image_analysis['alt_ratio'] < 0.5:
            score -= 30
        elif image_analysis['alt_ratio'] < 0.8:
            score -= 15
        
        image_analysis['image_score'] = max(0, score)
        
        return image_analysis
    
    async def _analyze_links(self, crawl_data: Dict[str, Any], target_url: str) -> Dict[str, Any]:
        """分析链接结构"""
        links = crawl_data.get('links', [])
        target_domain = urlparse(target_url).netloc
        
        link_analysis = {
            'total_links': len(links),
            'internal_links': 0,
            'external_links': 0,
            'internal_ratio': 0,
            'issues': [],
            'link_score': 0
        }
        
        if links:
            # 分类内部和外部链接
            for link in links:
                href = link.get('href', '')
                if href:
                    # 处理相对链接
                    if href.startswith('/') or href.startswith('#') or not href.startswith('http'):
                        link_analysis['internal_links'] += 1
                    else:
                        # 检查是否为同域名
                        link_domain = urlparse(href).netloc
                        if link_domain == target_domain:
                            link_analysis['internal_links'] += 1
                        else:
                            link_analysis['external_links'] += 1
            
            # 计算内部链接比例
            if link_analysis['total_links'] > 0:
                link_analysis['internal_ratio'] = link_analysis['internal_links'] / link_analysis['total_links']
            
            # 检查内部链接比例
            if link_analysis['internal_ratio'] < self.seo_rules['internal_link_ratio']:
                link_analysis['issues'].append({
                    'type': 'low_internal_links',
                    'severity': 'medium',
                    'message': f'内部链接比例 {link_analysis["internal_ratio"]:.1%} 过低，建议至少 {self.seo_rules["internal_link_ratio"]:.0%}',
                    'recommendation': '增加相关页面的内部链接，改善网站结构'
                })
            
            # 检查无文本链接
            empty_text_links = len([link for link in links if not link.get('text', '').strip()])
            if empty_text_links > 0:
                link_analysis['issues'].append({
                    'type': 'empty_link_text',
                    'severity': 'medium',
                    'message': f'{empty_text_links} 个链接缺少锚文本',
                    'recommendation': '为所有链接添加描述性的锚文本'
                })
        
        # 计算链接分数
        score = 100
        if link_analysis['internal_ratio'] < 0.1:
            score -= 20
        score -= len([issue for issue in link_analysis['issues'] if issue['severity'] == 'medium']) * 10
        
        link_analysis['link_score'] = max(0, score)
        
        return link_analysis
    
    async def _analyze_mobile_friendliness(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析移动端友好性"""
        # 这里需要实际的移动端测试数据
        # 目前基于可用数据进行基础分析
        
        mobile_analysis = {
            'has_viewport_meta': True,  # 需要从 HTML 中检查
            'responsive_design': True,  # 需要实际测试
            'mobile_speed': None,  # 需要移动端性能数据
            'touch_friendly': True,  # 需要实际测试
            'issues': [],
            'mobile_score': 85  # 默认分数
        }
        
        # 基于页面加载时间推断移动端性能
        load_time = crawl_data.get('load_time', 0)
        if load_time > 5.0:  # 移动端阈值更严格
            mobile_analysis['issues'].append({
                'type': 'slow_mobile_loading',
                'severity': 'high',
                'message': f'页面加载时间 {load_time:.2f}s 对移动端用户过慢',
                'recommendation': '优化移动端性能，压缩资源，使用响应式图片'
            })
            mobile_analysis['mobile_score'] -= 20
        
        return mobile_analysis
    
    async def _analyze_schema_markup(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析结构化数据标记"""
        schema_data = crawl_data.get('schema_org', [])
        
        schema_analysis = {
            'has_schema': len(schema_data) > 0,
            'schema_types': [],
            'schema_count': len(schema_data),
            'issues': [],
            'schema_score': 0
        }
        
        if schema_data:
            # 提取 schema 类型
            for schema in schema_data:
                if isinstance(schema, dict) and '@type' in schema:
                    schema_type = schema['@type']
                    if isinstance(schema_type, list):
                        schema_analysis['schema_types'].extend(schema_type)
                    else:
                        schema_analysis['schema_types'].append(schema_type)
            
            schema_analysis['schema_types'] = list(set(schema_analysis['schema_types']))
            schema_analysis['schema_score'] = 100
        else:
            schema_analysis['issues'].append({
                'type': 'missing_schema',
                'severity': 'medium',
                'message': '页面缺少结构化数据标记',
                'recommendation': '添加适当的 Schema.org 标记提升搜索结果展示'
            })
            schema_analysis['schema_score'] = 0
        
        return schema_analysis
    
    async def _calculate_technical_score(self, audit_data: Dict[str, Any]) -> int:
        """计算总体技术 SEO 分数"""
        scores = []
        weights = {
            'page_performance': 0.25,
            'html_structure': 0.15,
            'meta_tags': 0.20,
            'heading_structure': 0.15,
            'images_analysis': 0.10,
            'links_analysis': 0.10,
            'mobile_friendliness': 0.05
        }
        
        for category, weight in weights.items():
            if category in audit_data:
                category_data = audit_data[category]
                if isinstance(category_data, dict):
                    # 查找分数字段
                    score_field = f"{category.split('_')[0]}_score"
                    if score_field in category_data:
                        scores.append(category_data[score_field] * weight)
                    elif 'score' in category_data:
                        scores.append(category_data['score'] * weight)
        
        return int(sum(scores)) if scores else 0
    
    async def _generate_technical_recommendations(self, audit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成技术优化建议"""
        recommendations = []
        
        # 收集所有问题
        all_issues = []
        for category, data in audit_data.items():
            if isinstance(data, dict) and 'issues' in data:
                for issue in data['issues']:
                    issue['category'] = category
                    all_issues.append(issue)
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        # 转换为建议格式
        for issue in all_issues[:10]:  # 限制建议数量
            recommendations.append({
                'category': 'technical_seo',
                'priority': issue.get('severity', 'medium'),
                'title': issue.get('message', ''),
                'description': issue.get('recommendation', ''),
                'impact': self._severity_to_impact(issue.get('severity', 'medium')),
                'effort': 2,  # 默认工作量
                'issue_type': issue.get('type', 'unknown')
            })
        
        return recommendations
    
    async def _identify_critical_issues(self, audit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别关键问题"""
        critical_issues = []
        
        # 检查关键性能问题
        performance = audit_data.get('page_performance', {})
        if performance.get('load_time', 0) > 5.0:
            critical_issues.append({
                'type': 'performance',
                'severity': 'critical',
                'title': '页面加载速度过慢',
                'description': f"页面加载时间 {performance.get('load_time', 0):.2f}s 严重影响用户体验和搜索排名",
                'impact': 'high'
            })
        
        # 检查关键 HTML 问题
        meta_tags = audit_data.get('meta_tags', {})
        if not meta_tags.get('title', {}).get('content'):
            critical_issues.append({
                'type': 'meta',
                'severity': 'critical',
                'title': '缺少页面标题',
                'description': '页面标题是最重要的 SEO 元素之一，必须添加',
                'impact': 'high'
            })
        
        # 检查移动端问题
        mobile = audit_data.get('mobile_friendliness', {})
        if mobile.get('mobile_score', 100) < 60:
            critical_issues.append({
                'type': 'mobile',
                'severity': 'critical',
                'title': '移动端体验差',
                'description': '移动端优化不足，影响移动搜索排名',
                'impact': 'high'
            })
        
        return critical_issues
    
    def _severity_to_impact(self, severity: str) -> int:
        """将严重程度转换为影响分数"""
        mapping = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2
        }
        return mapping.get(severity, 3)
    
    def _estimate_tokens_used(self, crawl_data: Dict[str, Any]) -> int:
        """估算使用的 token 数量"""
        # 技术审计主要基于规则，AI 使用较少
        return 500
    
    def _estimate_cost(self, crawl_data: Dict[str, Any]) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(crawl_data)
        return tokens / 1000 * 0.03
