import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

async def scrape_article(url: str, max_retries: int = 3, retry_delay: int = 2) -> str:
    logger.info(f"Starting to scrape article from: {url}")
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            content, title = await _fetch_and_parse(url)
            logger.info(f"Successfully scraped article: {title if title else 'Untitled'}")
            return content
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when fetching {url}: {e.response.status_code}")
            if e.response.status_code >= 500 and retry_count < max_retries - 1:
                retry_count += 1
                logger.info(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue
            raise HTTPException(status_code=400, detail=f"Failed to fetch article: HTTP error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error when fetching {url}: {str(e)}")
            if retry_count < max_retries - 1:
                retry_count += 1
                logger.info(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue
            raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error when scraping {url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to scrape article: {str(e)}")

async def _fetch_and_parse(url: str) -> Tuple[str, Optional[str]]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else None
        
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            element.extract()
        
        main_content = None
        for tag in ["article", "main", "div.content", "div.post", "div.article"]:
            content_section = soup.select_one(tag)
            if content_section:
                main_content = content_section
                break
        
        if not main_content:
            main_content = soup.body
        
        text = main_content.get_text() if main_content else soup.get_text()
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if len(text) < 500:
            logger.warning(f"Scraped content from {url} is suspiciously short ({len(text)} chars)")
        
        return text, title
