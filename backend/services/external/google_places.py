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
    
    async def analyze_local_competition(self, business_name: str, location: str) -> Dict[str, Any]:
        """分析本地竞争情况"""
        if not self.api_key:
            return {"competitors": [], "analysis": {}}
        
        # 搜索同类企业
        competitors = await self.search_text(business_name, location)
        
        analysis = {
            "total_competitors": len(competitors),
            "avg_rating": 0,
            "top_competitors": [],
            "market_saturation": "low"
        }
        
        if competitors:
            # 计算平均评分
            ratings = [comp.get('rating', 0) for comp in competitors if comp.get('rating')]
            if ratings:
                analysis["avg_rating"] = sum(ratings) / len(ratings)
            
            # 获取前5个竞争对手
            sorted_competitors = sorted(
                competitors,
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
        
        return {
            "competitors": competitors,
            "analysis": analysis
        }
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.api_key is not None
