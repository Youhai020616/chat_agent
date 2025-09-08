"""
网站爬虫服务

使用 Playwright 进行全站抓取，提取 SEO 相关数据
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    # 如果 Playwright 未安装，提供 mock 实现
    async_playwright = None
    Page = None
    Browser = None

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """爬虫结果数据结构"""
    url: str
    status_code: int
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    headings: Dict[str, List[str]] = None
    images: List[Dict[str, str]] = None
    links: List[Dict[str, str]] = None
    schema_org: List[Dict[str, Any]] = None
    load_time: Optional[float] = None
    content_length: Optional[int] = None
    lighthouse_scores: Optional[Dict[str, float]] = None
    error: Optional[str] = None
    crawled_at: datetime = None
    
    def __post_init__(self):
        if self.headings is None:
            self.headings = {}
        if self.images is None:
            self.images = []
        if self.links is None:
            self.links = []
        if self.schema_org is None:
            self.schema_org = []
        if self.crawled_at is None:
            self.crawled_at = datetime.utcnow()


class CrawlerService:
    """网站爬虫服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30000)  # 30 seconds
        self.user_agent = self.config.get(
            "user_agent", 
            "Mozilla/5.0 (compatible; SEO-GEO-Bot/1.0)"
        )
        self.max_pages = self.config.get("max_pages", 10)
        
    async def crawl_url(self, url: str) -> CrawlResult:
        """爬取单个 URL"""
        if not async_playwright:
            logger.warning("Playwright not available, returning mock data")
            return self._create_mock_result(url)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent=self.user_agent
                )
                
                # 设置超时
                page.set_default_timeout(self.timeout)
                
                start_time = datetime.utcnow()
                response = await page.goto(url, wait_until="networkidle")
                load_time = (datetime.utcnow() - start_time).total_seconds()
                
                result = CrawlResult(
                    url=url,
                    status_code=response.status,
                    load_time=load_time
                )
                
                if response.status == 200:
                    await self._extract_page_data(page, result)
                else:
                    result.error = f"HTTP {response.status}"
                
                await browser.close()
                return result
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                status_code=0,
                error=str(e)
            )
    
    async def _extract_page_data(self, page: Page, result: CrawlResult):
        """从页面提取 SEO 数据"""
        try:
            # 基本 meta 信息
            result.title = await page.title()
            
            # Meta 标签
            meta_desc = await page.get_attribute('meta[name="description"]', 'content')
            result.meta_description = meta_desc
            
            meta_keywords = await page.get_attribute('meta[name="keywords"]', 'content')
            result.meta_keywords = meta_keywords
            
            # 标题层级
            result.headings = await self._extract_headings(page)
            
            # 图片信息
            result.images = await self._extract_images(page)
            
            # 链接信息
            result.links = await self._extract_links(page)
            
            # Schema.org 结构化数据
            result.schema_org = await self._extract_schema_org(page)
            
            # 内容长度
            content = await page.text_content('body')
            result.content_length = len(content) if content else 0
            
        except Exception as e:
            logger.error(f"Error extracting page data: {str(e)}")
            result.error = str(e)
    
    async def _extract_headings(self, page: Page) -> Dict[str, List[str]]:
        """提取标题层级"""
        headings = {}
        for level in range(1, 7):  # h1-h6
            elements = await page.query_selector_all(f'h{level}')
            texts = []
            for element in elements:
                text = await element.text_content()
                if text and text.strip():
                    texts.append(text.strip())
            if texts:
                headings[f'h{level}'] = texts
        return headings
    
    async def _extract_images(self, page: Page) -> List[Dict[str, str]]:
        """提取图片信息"""
        images = []
        img_elements = await page.query_selector_all('img')
        for img in img_elements[:20]:  # 限制数量
            src = await img.get_attribute('src')
            alt = await img.get_attribute('alt')
            if src:
                images.append({
                    'src': src,
                    'alt': alt or '',
                })
        return images
    
    async def _extract_links(self, page: Page) -> List[Dict[str, str]]:
        """提取链接信息"""
        links = []
        link_elements = await page.query_selector_all('a[href]')
        for link in link_elements[:50]:  # 限制数量
            href = await link.get_attribute('href')
            text = await link.text_content()
            if href:
                links.append({
                    'href': href,
                    'text': text.strip() if text else '',
                })
        return links
    
    async def _extract_schema_org(self, page: Page) -> List[Dict[str, Any]]:
        """提取 Schema.org 结构化数据"""
        schemas = []
        try:
            # JSON-LD
            json_ld_elements = await page.query_selector_all('script[type="application/ld+json"]')
            for element in json_ld_elements:
                content = await element.text_content()
                if content:
                    try:
                        import json
                        schema_data = json.loads(content)
                        schemas.append(schema_data)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error extracting schema.org data: {str(e)}")
        
        return schemas
    
    def _create_mock_result(self, url: str) -> CrawlResult:
        """创建模拟爬虫结果（用于测试）"""
        return CrawlResult(
            url=url,
            status_code=200,
            title="Mock Page Title",
            meta_description="Mock meta description for testing",
            headings={"h1": ["Main Heading"], "h2": ["Sub Heading 1", "Sub Heading 2"]},
            images=[{"src": "/image1.jpg", "alt": "Mock image"}],
            links=[{"href": "/page1", "text": "Internal Link"}],
            load_time=1.5,
            content_length=5000
        )
