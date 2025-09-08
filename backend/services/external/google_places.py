"""
Google Places API 服务

提供地理位置查询、本地企业信息等功能
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Google Places API 服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = self.config.get('google_api_key')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        if not self.api_key:
            logger.warning("Google API key not provided, service will be disabled")
    
    async def search_nearby(
        self,
        location: str,
        radius: int = 5000,
        place_type: str = "establishment",
        keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索附近的地点"""
        if not self.api_key:
            return []
        
        # 首先获取位置坐标
        coordinates = await self.geocode(location)
        if not coordinates:
            return []
        
        url = f"{self.base_url}/nearbysearch/json"
        params = {
            'location': f"{coordinates['lat']},{coordinates['lng']}",
            'radius': radius,
            'type': place_type,
            'key': self.api_key
        }
        
        if keyword:
            params['keyword'] = keyword
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('results', [])
                    else:
                        logger.error(f"Google Places API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Google Places search failed: {str(e)}")
            return []
    
    async def geocode(self, address: str) -> Optional[Dict[str, float]]:
        """地址转坐标"""
        if not self.api_key:
            return None
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        if results:
                            location = results[0]['geometry']['location']
                            return {
                                'lat': location['lat'],
                                'lng': location['lng']
                            }
                    return None
                    
        except Exception as e:
            logger.error(f"Geocoding failed: {str(e)}")
            return None
    
    async def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """获取地点详细信息"""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,rating,reviews,formatted_address,formatted_phone_number,website,opening_hours,geometry',
            'key': self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result')
                    return None
                    
        except Exception as e:
            logger.error(f"Place details fetch failed: {str(e)}")
            return None
    
    async def search_text(self, query: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """文本搜索地点"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/textsearch/json"
        params = {
            'query': query,
            'key': self.api_key
        }
        
        if location:
            coordinates = await self.geocode(location)
            if coordinates:
                params['location'] = f"{coordinates['lat']},{coordinates['lng']}"
                params['radius'] = 10000  # 10km radius
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('results', [])
                    return []
                    
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")
            return []
    
    async def analyze_local_competition(self, business_type: str, location: str) -> Dict[str, Any]:
        """分析本地竞争情况"""
        if not self.api_key:
            return {"competitors": [], "analysis": {}}

        # 搜索同类企业
        competitors = await self.search_text(f"{business_type} {location}", location)

        analysis = {
            "total_competitors": len(competitors),
            "avg_rating": 0,
            "avg_reviews": 0,
            "top_competitors": [],
            "market_saturation": "low",
            "competitive_landscape": "low"
        }

        if competitors:
            # 计算平均评分和评论数
            ratings = [comp.get('rating', 0) for comp in competitors if comp.get('rating')]
            reviews = [comp.get('user_ratings_total', 0) for comp in competitors if comp.get('user_ratings_total')]

            if ratings:
                analysis["avg_rating"] = sum(ratings) / len(ratings)
            if reviews:
                analysis["avg_reviews"] = sum(reviews) / len(reviews)

            # 获取前5个竞争对手，增加关键词匹配
            enhanced_competitors = []
            for comp in competitors:
                # 为每个竞争对手添加关键词分析
                comp_enhanced = comp.copy()
                comp_enhanced['keywords'] = self._extract_business_keywords(comp.get('name', ''))
                comp_enhanced['total_appearances'] = 1  # 简化处理
                enhanced_competitors.append(comp_enhanced)

            sorted_competitors = sorted(
                enhanced_competitors,
                key=lambda x: (x.get('rating', 0), x.get('user_ratings_total', 0)),
                reverse=True
            )

            analysis["top_competitors"] = sorted_competitors[:5]

            # 评估市场饱和度
            if len(competitors) > 20:
                analysis["market_saturation"] = "high"
            elif len(competitors) > 10:
                analysis["market_saturation"] = "medium"
            else:
                analysis["market_saturation"] = "low"

            # 评估竞争环境
            high_quality_competitors = len([
                c for c in competitors
                if c.get('rating', 0) > 4.0 and c.get('user_ratings_total', 0) > 50
            ])

            if len(competitors) > 15 and high_quality_competitors > 5:
                analysis["competitive_landscape"] = "very_high"
            elif len(competitors) > 10 and high_quality_competitors > 3:
                analysis["competitive_landscape"] = "high"
            elif len(competitors) > 5:
                analysis["competitive_landscape"] = "medium"
            else:
                analysis["competitive_landscape"] = "low"

        return {
            "competitors": competitors,
            "analysis": analysis
        }

    def _extract_business_keywords(self, business_name: str) -> List[Dict[str, Any]]:
        """从企业名称中提取关键词"""
        # 简化的关键词提取
        keywords = []
        words = business_name.split()

        for word in words:
            if len(word) > 2:  # 忽略过短的词
                keywords.append({
                    'keyword': word,
                    'position': 1,  # 简化处理
                    'relevance': 'high'
                })

        return keywords

    async def get_place_reviews(self, place_id: str) -> List[Dict[str, Any]]:
        """获取地点评论"""
        details = await self.get_place_details(place_id)
        if details and 'reviews' in details:
            return details['reviews']
        return []

    async def analyze_reviews_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析评论情感"""
        if not reviews:
            return {
                'sentiment_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'common_themes': []
            }

        # 简化的情感分析
        positive_keywords = ['好', '棒', '优秀', '满意', '推荐', 'good', 'great', 'excellent']
        negative_keywords = ['差', '糟糕', '失望', '不满', '不推荐', 'bad', 'terrible', 'disappointed']

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for review in reviews:
            text = review.get('text', '').lower()

            positive_score = sum(1 for keyword in positive_keywords if keyword in text)
            negative_score = sum(1 for keyword in negative_keywords if keyword in text)

            if positive_score > negative_score:
                positive_count += 1
            elif negative_score > positive_score:
                negative_count += 1
            else:
                neutral_count += 1

        total_reviews = len(reviews)
        sentiment_score = (positive_count - negative_count) / total_reviews if total_reviews > 0 else 0

        return {
            'sentiment_score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_reviews': total_reviews,
            'common_themes': self._extract_common_themes(reviews)
        }

    def _extract_common_themes(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """提取评论中的常见主题"""
        themes = []

        # 服务相关主题
        service_keywords = ['服务', '态度', '专业', 'service', 'staff']
        quality_keywords = ['质量', '效果', '结果', 'quality', 'result']
        price_keywords = ['价格', '费用', '性价比', 'price', 'cost']

        service_mentions = 0
        quality_mentions = 0
        price_mentions = 0

        for review in reviews:
            text = review.get('text', '').lower()

            if any(keyword in text for keyword in service_keywords):
                service_mentions += 1
            if any(keyword in text for keyword in quality_keywords):
                quality_mentions += 1
            if any(keyword in text for keyword in price_keywords):
                price_mentions += 1

        if service_mentions > len(reviews) * 0.3:
            themes.append('服务质量')
        if quality_mentions > len(reviews) * 0.3:
            themes.append('产品质量')
        if price_mentions > len(reviews) * 0.3:
            themes.append('价格因素')

        return themes
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.api_key is not None
