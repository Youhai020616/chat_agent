"""
OpenAI API 服务

提供 GPT 模型的聊天完成、文本分析等功能
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API 服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = self.config.get('openai_api_key')
        self.model = self.config.get('openai_model', 'gpt-4')
        self.temperature = self.config.get('openai_temperature', 0.1)
        self.max_tokens = self.config.get('openai_max_tokens', 2000)
        
        self.client: Optional[AsyncOpenAI] = None
        
        if self.api_key and AsyncOpenAI:
            self.client = AsyncOpenAI(api_key=self.api_key)
        elif not self.api_key:
            logger.warning("OpenAI API key not provided, service will be disabled")
        elif not AsyncOpenAI:
            logger.warning("OpenAI library not installed, service will be disabled")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """聊天完成 API 调用"""
        if not self.client:
            raise ValueError("OpenAI client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {str(e)}")
            raise
    
    async def analyze_content_sentiment(self, content: str) -> Dict[str, Any]:
        """分析内容情感"""
        if not self.client:
            return {"sentiment": "neutral", "confidence": 0.5}
        
        prompt = f"""
        请分析以下内容的情感倾向，返回 JSON 格式：
        {{
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0,
            "keywords": ["关键词1", "关键词2"]
        }}
        
        内容：
        {content[:1000]}
        """
        
        try:
            response = await self.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.5}
    
    async def extract_keywords(self, content: str, count: int = 10) -> List[str]:
        """提取关键词"""
        if not self.client:
            return []
        
        prompt = f"""
        从以下内容中提取 {count} 个最重要的关键词，以逗号分隔返回：
        
        {content[:1500]}
        """
        
        try:
            response = await self.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            keywords = [kw.strip() for kw in response.split(',')]
            return keywords[:count]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def generate_meta_description(self, title: str, content: str) -> str:
        """生成 Meta Description"""
        if not self.client:
            return ""
        
        prompt = f"""
        基于以下标题和内容，生成一个150-160字符的 Meta Description：
        
        标题：{title}
        内容：{content[:500]}
        
        要求：
        1. 包含主要关键词
        2. 吸引用户点击
        3. 准确描述页面内容
        4. 长度控制在150-160字符
        """
        
        try:
            response = await self.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Meta description generation failed: {str(e)}")
            return ""
    
    async def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """分析内容质量"""
        if not self.client:
            return {"score": 5, "suggestions": []}
        
        prompt = f"""
        请分析以下内容的质量，返回 JSON 格式：
        {{
            "score": 1-10,
            "readability": "easy/medium/hard",
            "suggestions": ["建议1", "建议2"],
            "strengths": ["优点1", "优点2"],
            "weaknesses": ["缺点1", "缺点2"]
        }}
        
        内容：
        {content[:1000]}
        """
        
        try:
            response = await self.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {str(e)}")
            return {"score": 5, "suggestions": []}
    
    async def generate_seo_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成 SEO 优化建议"""
        if not self.client:
            return []
        
        prompt = f"""
        基于以下 SEO 分析数据，生成具体的优化建议，返回 JSON 数组格式：
        [
            {{
                "category": "技术SEO/内容优化/关键词优化",
                "title": "建议标题",
                "description": "详细描述",
                "priority": "high/medium/low",
                "impact": 1-5,
                "effort": 1-5
            }}
        ]
        
        分析数据：
        {json.dumps(analysis_data, ensure_ascii=False)[:2000]}
        """
        
        try:
            response = await self.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"SEO recommendations generation failed: {str(e)}")
            return []
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.client is not None
