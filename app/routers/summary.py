from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..schemas.summary import SummarizeRequest, SummaryResponse, SummaryListResponse
from ..services.web3_service import verify_signature
from ..services.scraper_service import scrape_article
from ..services.summarizer_service import summarizer
from ..services.summary_repository import SummaryRepository
from ..database import get_db

router = APIRouter(tags=["summaries"])
logger = logging.getLogger(__name__)

@router.post("/summarize", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def summarize_article(
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Summarize request received for article: {request.article_url}")
    
    is_valid = await verify_signature(request.wallet_address, request.signature)
    if not is_valid:
        logger.warning(f"Invalid signature from wallet: {request.wallet_address}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    logger.info(f"Scraping article from URL: {request.article_url}")
    article_content = await scrape_article(str(request.article_url))
    
    logger.info("Generating summary using AI service")
    summary_content = await summarizer.summarize_text(article_content)
    
    logger.info("Storing summary in the database")
    repository = SummaryRepository(db)
    summary = await repository.create_summary(
        wallet_address=request.wallet_address,
        article_url=str(request.article_url),
        original_content=article_content,
        summary_content=summary_content
    )
    
    logger.info(f"Summary created with ID: {summary.id}")
    return summary

@router.get("/summaries/{wallet_address}", response_model=SummaryListResponse)
async def get_summaries_by_wallet(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Fetching summaries for wallet: {wallet_address}")
    repository = SummaryRepository(db)
    summaries = await repository.get_summaries_by_wallet(wallet_address)
    
    logger.info(f"Retrieved {len(summaries)} summaries for wallet: {wallet_address}")
    return SummaryListResponse(summaries=summaries)
