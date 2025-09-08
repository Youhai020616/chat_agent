"""
SERP API 服务

提供搜索引擎结果页面数据
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class SERPAPIService:
    """SERP API 服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = self.config.get('serp_api_key')
        self.base_url = "https://serpapi.com/search"
        
        if not self.api_key:
            logger.warning("SERP API key not provided, service will be disabled")
    
    async def search(
        self,
        query: str,
        locale: str = "zh-CN",
        location: Optional[str] = None,
        device: str = "desktop"
    ) -> Optional[Dict[str, Any]]:
        """执行搜索查询"""
        if not self.api_key:
            return None
        
        params = {
            'q': query,
            'api_key': self.api_key,
            'engine': 'google',
            'hl': locale.split('-')[0],  # 语言代码
            'gl': locale.split('-')[1] if '-' in locale else 'CN',  # 国家代码
            'device': device,
            'num': 20  # 返回结果数量
        }
        
        if location:
            params['location'] = location
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"SERP API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"SERP API search failed: {str(e)}")
            return None
    
    async def search_local(
        self,
        query: str,
        location: str,
        locale: str = "zh-CN"
    ) -> Optional[Dict[str, Any]]:
        """本地搜索"""
        return await self.search(
            query=f"{query} {location}",
            locale=locale,
            location=location
        )
    
    async def get_related_searches(self, query: str, locale: str = "zh-CN") -> List[str]:
        """获取相关搜索"""
        search_result = await self.search(query, locale)
        
        if not search_result:
            return []
        
        related_searches = []
        
        # 从相关搜索部分提取
        if 'related_searches' in search_result:
            for item in search_result['related_searches']:
                if isinstance(item, dict) and 'query' in item:
                    related_searches.append(item['query'])
        
        # 从人们还搜索部分提取
        if 'people_also_ask' in search_result:
            for item in search_result['people_also_ask']:
                if isinstance(item, dict) and 'question' in item:
                    related_searches.append(item['question'])
        
        return related_searches[:10]  # 限制数量
    
    async def analyze_serp_features(self, query: str, locale: str = "zh-CN") -> Dict[str, Any]:
        """分析 SERP 特征"""
        search_result = await self.search(query, locale)
        
        if not search_result:
            return {}
        
        features = {
            'has_ads': bool(search_result.get('ads')),
            'has_local_results': bool(search_result.get('local_results')),
            'has_knowledge_graph': bool(search_result.get('knowledge_graph')),
            'has_featured_snippet': bool(search_result.get('featured_snippet')),
            'has_image_results': bool(search_result.get('images_results')),
            'has_video_results': bool(search_result.get('video_results')),
            'has_shopping_results': bool(search_result.get('shopping_results')),
            'has_news_results': bool(search_result.get('news_results')),
            'organic_results_count': len(search_result.get('organic_results', [])),
            'total_results': search_result.get('search_information', {}).get('total_results', 0)
        }
        
        return features
    
    async def track_rankings(
        self,
        keywords: List[str],
        domain: str,
        locale: str = "zh-CN",
        location: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """跟踪关键词排名"""
        rankings = {}
        
        for keyword in keywords:
            search_result = await self.search(keyword, locale, location)
            
            if not search_result:
                rankings[keyword] = {'position': None, 'url': None}
                continue
            
            # 在自然搜索结果中查找域名
            organic_results = search_result.get('organic_results', [])
            position = None
            url = None
            
            for i, result in enumerate(organic_results):
                result_url = result.get('link', '')
                if domain.lower() in result_url.lower():
                    position = i + 1
                    url = result_url
                    break
            
            rankings[keyword] = {
                'position': position,
                'url': url,
                'total_results': search_result.get('search_information', {}).get('total_results', 0),
                'has_local_pack': bool(search_result.get('local_results')),
                'competition_level': self._assess_competition(search_result)
            }
            
            # 添加延迟避免 API 限制
            await asyncio.sleep(1)
        
        return rankings
    
    async def competitor_analysis(
        self,
        keywords: List[str],
        locale: str = "zh-CN",
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """竞争对手分析"""
        competitor_data = {}
        domain_rankings = {}
        
        for keyword in keywords:
            search_result = await self.search(keyword, locale, location)
            
            if not search_result:
                continue
            
            organic_results = search_result.get('organic_results', [])
            
            for i, result in enumerate(organic_results[:10]):  # 只分析前10个结果
                domain = self._extract_domain(result.get('link', ''))
                if not domain:
                    continue
                
                if domain not in domain_rankings:
                    domain_rankings[domain] = {
                        'domain': domain,
                        'keywords': [],
                        'avg_position': 0,
                        'total_appearances': 0
                    }
                
                domain_rankings[domain]['keywords'].append({
                    'keyword': keyword,
                    'position': i + 1,
                    'title': result.get('title', ''),
                    'url': result.get('link', '')
                })
                domain_rankings[domain]['total_appearances'] += 1
            
            await asyncio.sleep(1)  # API 限制
        
        # 计算平均排名
        for domain_data in domain_rankings.values():
            positions = [kw['position'] for kw in domain_data['keywords']]
            domain_data['avg_position'] = sum(positions) / len(positions) if positions else 0
        
        # 按出现次数排序
        sorted_competitors = sorted(
            domain_rankings.values(),
            key=lambda x: x['total_appearances'],
            reverse=True
        )
        
        return {
            'top_competitors': sorted_competitors[:10],
            'total_domains': len(domain_rankings),
            'analyzed_keywords': len(keywords)
        }
    
    def _assess_competition(self, search_result: Dict[str, Any]) -> str:
        """评估竞争水平"""
        score = 0
        
        # 广告数量
        ads_count = len(search_result.get('ads', []))
        if ads_count > 3:
            score += 30
        elif ads_count > 0:
            score += 15
        
        # 特殊结果
        if search_result.get('featured_snippet'):
            score += 20
        if search_result.get('knowledge_graph'):
            score += 15
        if search_result.get('local_results'):
            score += 25
        
        # 总结果数
        total_results = search_result.get('search_information', {}).get('total_results', 0)
        if total_results > 1000000:
            score += 10
        
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _extract_domain(self, url: str) -> str:
        """从 URL 提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.api_key is not None
