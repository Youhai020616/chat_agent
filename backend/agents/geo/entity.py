"""
Entity Agent - 实体识别和地理信息提取

功能：
1. 从网站内容中识别地理实体（城市、地区、地标等）
2. 提取业务实体信息（公司名称、地址、联系方式）
3. 分析 NAP（Name, Address, Phone）一致性
4. 识别服务区域和目标市场
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

from ..base import BaseAgent, AgentResult
from ...services.external.openai_service import OpenAIService
from ...services.external.google_places import GooglePlacesService

logger = logging.getLogger(__name__)


class EntityAgent(BaseAgent):
    """实体识别和地理信息提取 Agent"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("entity", config)
        self.openai_service = OpenAIService(config)
        self.places_service = GooglePlacesService(config)
        
        # 地理实体识别模式
        self.geo_patterns = {
            'cities': r'\b(?:北京|上海|广州|深圳|杭州|南京|成都|武汉|西安|重庆|天津|青岛|大连|厦门|苏州|无锡|宁波|佛山|东莞|中山|珠海|惠州|江门|肇庆|汕头|潮州|揭阳|梅州|河源|清远|韶关|云浮|阳江|茂名|湛江|海口|三亚|儋州|琼海|文昌|万宁|五指山|东方|定安|屯昌|澄迈|临高|白沙|昌江|乐东|陵水|保亭|琼中|西沙|南沙|中沙)\b',
            'provinces': r'\b(?:北京市|天津市|河北省|山西省|内蒙古|辽宁省|吉林省|黑龙江省|上海市|江苏省|浙江省|安徽省|福建省|江西省|山东省|河南省|湖北省|湖南省|广东省|广西|海南省|重庆市|四川省|贵州省|云南省|西藏|陕西省|甘肃省|青海省|宁夏|新疆|香港|澳门|台湾)\b',
            'districts': r'\b(?:区|县|市|镇|街道|开发区|高新区|经济区)\b',
            'landmarks': r'\b(?:广场|公园|商场|医院|学校|大学|车站|机场|港口|景区|博物馆|图书馆|体育馆|剧院|银行|酒店|宾馆)\b'
        }
        
        # NAP 识别模式
        self.nap_patterns = {
            'phone': r'(?:电话|手机|联系电话|客服电话|热线)[:：]?\s*([0-9\-\s\(\)]{8,20})',
            'address': r'(?:地址|位置|所在地)[:：]?\s*([^，。；\n]{10,100})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'website': r'(?:网站|官网|网址)[:：]?\s*(https?://[^\s]+)',
        }
    
    async def analyze(self, state: "SEOState") -> AgentResult:
        """执行实体识别和地理信息提取"""
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
            
            # 提取文本内容
            content_text = self._extract_content_text(crawl_data)
            
            # 并行执行各种分析
            tasks = [
                self._extract_geographic_entities(content_text),
                self._extract_business_entities(content_text, crawl_data),
                self._analyze_nap_consistency(content_text, crawl_data),
                self._identify_service_areas(content_text),
                self._extract_schema_entities(crawl_data.get('schema_org', []))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合结果
            analysis_data = {
                'geographic_entities': results[0] if not isinstance(results[0], Exception) else {},
                'business_entities': results[1] if not isinstance(results[1], Exception) else {},
                'nap_analysis': results[2] if not isinstance(results[2], Exception) else {},
                'service_areas': results[3] if not isinstance(results[3], Exception) else [],
                'schema_entities': results[4] if not isinstance(results[4], Exception) else {},
                'analysis_metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'content_length': len(content_text),
                    'url': state.target_url,
                    'locale': state.locale
                }
            }
            
            # 生成地理优化建议
            recommendations = await self._generate_geo_recommendations(analysis_data)
            analysis_data['recommendations'] = recommendations
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                success=True,
                data=analysis_data,
                execution_time=execution_time,
                tokens_used=self._estimate_tokens_used(content_text),
                cost=self._estimate_cost(content_text)
            )
            
        except Exception as e:
            logger.error(f"Entity analysis failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    def _extract_content_text(self, crawl_data: Dict[str, Any]) -> str:
        """从爬虫数据中提取文本内容"""
        content_parts = []
        
        # 标题
        if crawl_data.get('title'):
            content_parts.append(crawl_data['title'])
        
        # Meta 描述
        if crawl_data.get('meta_description'):
            content_parts.append(crawl_data['meta_description'])
        
        # 标题层级
        headings = crawl_data.get('headings', {})
        for level, texts in headings.items():
            content_parts.extend(texts)
        
        # 图片 alt 文本
        images = crawl_data.get('images', [])
        for img in images:
            if img.get('alt'):
                content_parts.append(img['alt'])
        
        # 链接文本
        links = crawl_data.get('links', [])
        for link in links:
            if link.get('text'):
                content_parts.append(link['text'])
        
        return ' '.join(content_parts)
    
    async def _extract_geographic_entities(self, content: str) -> Dict[str, List[str]]:
        """提取地理实体"""
        entities = {}
        
        for entity_type, pattern in self.geo_patterns.items():
            matches = re.findall(pattern, content)
            entities[entity_type] = list(set(matches))  # 去重
        
        # 使用 AI 进一步识别地理实体
        if self.openai_service:
            try:
                ai_entities = await self._ai_extract_geographic_entities(content)
                # 合并 AI 识别的结果
                for entity_type, ai_matches in ai_entities.items():
                    if entity_type in entities:
                        entities[entity_type].extend(ai_matches)
                        entities[entity_type] = list(set(entities[entity_type]))
                    else:
                        entities[entity_type] = ai_matches
            except Exception as e:
                logger.warning(f"AI geographic entity extraction failed: {str(e)}")
        
        return entities
    
    async def _extract_business_entities(self, content: str, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取业务实体信息"""
        business_info = {
            'company_names': [],
            'contact_info': {},
            'business_hours': [],
            'services': []
        }
        
        # 从 Schema.org 数据中提取
        schema_data = crawl_data.get('schema_org', [])
        for schema in schema_data:
            if isinstance(schema, dict):
                schema_type = schema.get('@type', '').lower()
                if 'organization' in schema_type or 'localbusiness' in schema_type:
                    if schema.get('name'):
                        business_info['company_names'].append(schema['name'])
                    if schema.get('telephone'):
                        business_info['contact_info']['phone'] = schema['telephone']
                    if schema.get('address'):
                        business_info['contact_info']['address'] = schema['address']
        
        # 使用正则表达式提取联系信息
        for info_type, pattern in self.nap_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                business_info['contact_info'][info_type] = matches[0] if len(matches) == 1 else matches
        
        return business_info
    
    async def _analyze_nap_consistency(self, content: str, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析 NAP（Name, Address, Phone）一致性"""
        nap_data = {
            'name_variations': [],
            'address_variations': [],
            'phone_variations': [],
            'consistency_score': 0.0,
            'issues': []
        }
        
        # 提取所有 NAP 信息
        names = set()
        addresses = set()
        phones = set()
        
        # 从不同来源提取
        schema_data = crawl_data.get('schema_org', [])
        for schema in schema_data:
            if isinstance(schema, dict):
                if schema.get('name'):
                    names.add(schema['name'])
                if schema.get('address'):
                    addr = schema['address']
                    if isinstance(addr, dict):
                        addr_str = f"{addr.get('streetAddress', '')} {addr.get('addressLocality', '')} {addr.get('addressRegion', '')}"
                        addresses.add(addr_str.strip())
                    elif isinstance(addr, str):
                        addresses.add(addr)
                if schema.get('telephone'):
                    phones.add(schema['telephone'])
        
        # 从文本内容中提取
        for pattern_type, pattern in self.nap_patterns.items():
            matches = re.findall(pattern, content)
            if pattern_type == 'phone':
                phones.update(matches)
            elif pattern_type == 'address':
                addresses.update(matches)
        
        nap_data['name_variations'] = list(names)
        nap_data['address_variations'] = list(addresses)
        nap_data['phone_variations'] = list(phones)
        
        # 计算一致性分数
        consistency_issues = 0
        if len(names) > 1:
            consistency_issues += 1
            nap_data['issues'].append("发现多个不同的公司名称")
        if len(addresses) > 1:
            consistency_issues += 1
            nap_data['issues'].append("发现多个不同的地址信息")
        if len(phones) > 1:
            consistency_issues += 1
            nap_data['issues'].append("发现多个不同的电话号码")
        
        # 计算一致性分数（0-100）
        total_checks = 3
        nap_data['consistency_score'] = max(0, (total_checks - consistency_issues) / total_checks * 100)
        
        return nap_data
    
    async def _identify_service_areas(self, content: str) -> List[Dict[str, Any]]:
        """识别服务区域"""
        service_areas = []
        
        # 查找服务区域关键词
        service_keywords = ['服务', '覆盖', '业务范围', '服务区域', '配送范围', '营业区域']
        area_keywords = ['市', '区', '县', '镇', '街道', '周边', '附近']
        
        for keyword in service_keywords:
            # 查找包含服务关键词的句子
            pattern = f'[^。！？]*{keyword}[^。！？]*'
            matches = re.findall(pattern, content)
            
            for match in matches:
                # 在匹配的句子中查找地理区域
                areas = []
                for area_keyword in area_keywords:
                    area_pattern = f'[^，。；\s]*{area_keyword}'
                    area_matches = re.findall(area_pattern, match)
                    areas.extend(area_matches)
                
                if areas:
                    service_areas.append({
                        'description': match.strip(),
                        'areas': list(set(areas)),
                        'keyword': keyword
                    })
        
        return service_areas
    
    async def _extract_schema_entities(self, schema_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从 Schema.org 数据中提取实体信息"""
        entities = {
            'organizations': [],
            'places': [],
            'events': [],
            'products': []
        }
        
        for schema in schema_data:
            if not isinstance(schema, dict):
                continue
            
            schema_type = schema.get('@type', '').lower()
            
            if 'organization' in schema_type or 'localbusiness' in schema_type:
                entities['organizations'].append({
                    'name': schema.get('name'),
                    'type': schema.get('@type'),
                    'address': schema.get('address'),
                    'telephone': schema.get('telephone'),
                    'url': schema.get('url')
                })
            elif 'place' in schema_type:
                entities['places'].append({
                    'name': schema.get('name'),
                    'type': schema.get('@type'),
                    'address': schema.get('address'),
                    'geo': schema.get('geo')
                })
            elif 'event' in schema_type:
                entities['events'].append({
                    'name': schema.get('name'),
                    'type': schema.get('@type'),
                    'location': schema.get('location'),
                    'startDate': schema.get('startDate')
                })
            elif 'product' in schema_type:
                entities['products'].append({
                    'name': schema.get('name'),
                    'type': schema.get('@type'),
                    'brand': schema.get('brand'),
                    'offers': schema.get('offers')
                })
        
        return entities
    
    async def _ai_extract_geographic_entities(self, content: str) -> Dict[str, List[str]]:
        """使用 AI 提取地理实体"""
        if not self.openai_service:
            return {}
        
        prompt = f"""
        请从以下文本中提取地理相关的实体信息，包括：
        1. 城市名称
        2. 省份/地区名称
        3. 具体地址
        4. 地标建筑
        5. 商圈或区域名称
        
        文本内容：
        {content[:2000]}  # 限制长度避免超出 token 限制
        
        请以 JSON 格式返回结果：
        {{
            "cities": ["城市1", "城市2"],
            "provinces": ["省份1", "省份2"],
            "addresses": ["地址1", "地址2"],
            "landmarks": ["地标1", "地标2"],
            "areas": ["区域1", "区域2"]
        }}
        """
        
        try:
            response = await self.openai_service.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # 解析 JSON 响应
            import json
            result = json.loads(response)
            return result
            
        except Exception as e:
            logger.error(f"AI geographic entity extraction failed: {str(e)}")
            return {}
    
    async def _generate_geo_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成地理优化建议"""
        recommendations = []
        
        # NAP 一致性建议
        nap_analysis = analysis_data.get('nap_analysis', {})
        if nap_analysis.get('consistency_score', 100) < 90:
            recommendations.append({
                'category': 'nap_consistency',
                'priority': 'high',
                'title': '改善 NAP 信息一致性',
                'description': '发现公司名称、地址或电话号码存在不一致，建议统一所有平台上的 NAP 信息',
                'impact': 4,
                'effort': 3,
                'issues': nap_analysis.get('issues', [])
            })
        
        # 地理实体优化建议
        geo_entities = analysis_data.get('geographic_entities', {})
        if not geo_entities.get('cities') and not geo_entities.get('provinces'):
            recommendations.append({
                'category': 'geographic_targeting',
                'priority': 'medium',
                'title': '增加地理位置信息',
                'description': '网站内容中缺少明确的地理位置信息，建议在关键页面添加服务城市和地区信息',
                'impact': 3,
                'effort': 2
            })
        
        # Schema.org 结构化数据建议
        schema_entities = analysis_data.get('schema_entities', {})
        if not schema_entities.get('organizations'):
            recommendations.append({
                'category': 'structured_data',
                'priority': 'medium',
                'title': '添加本地企业结构化数据',
                'description': '建议添加 LocalBusiness Schema.org 标记，包含完整的 NAP 信息',
                'impact': 4,
                'effort': 3
            })
        
        # 服务区域建议
        service_areas = analysis_data.get('service_areas', [])
        if not service_areas:
            recommendations.append({
                'category': 'service_areas',
                'priority': 'low',
                'title': '明确服务区域',
                'description': '建议在网站上明确说明服务覆盖的地理区域，有助于本地搜索优化',
                'impact': 2,
                'effort': 2
            })
        
        return recommendations
    
    def _estimate_tokens_used(self, content: str) -> int:
        """估算使用的 token 数量"""
        # 简单估算：中文约 1.5 字符/token，英文约 4 字符/token
        return len(content) // 2
    
    def _estimate_cost(self, content: str) -> float:
        """估算 API 调用成本"""
        tokens = self._estimate_tokens_used(content)
        # GPT-4 价格约 $0.03/1K tokens
        return tokens / 1000 * 0.03
