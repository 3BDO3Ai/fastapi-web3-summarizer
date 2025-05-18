import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

async def scrape_article(url: str) -> str:
    """
    Scrape the content of an article from a given URL
    
    Args:
        url: The URL of the article to scrape
        
    Returns:
        str: The text content of the article
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            # Get text content
            text = soup.get_text()
            
            # Clean up text - remove extra whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch article: HTTP error {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape article: {str(e)}")
