from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from ..schemas.summary import SummarizeRequest, SummaryResponse, SummaryListResponse
from ..services.web3_service import verify_signature
from ..services.scraper_service import scrape_article
from ..services.summarizer_service import summarizer
from ..services.summary_repository import SummaryRepository
from ..database import get_db

router = APIRouter(tags=["summaries"])

@router.post("/summarize", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def summarize_article(
    request: SummarizeRequest,
    db: Session = Depends(get_db)
):
    # Verify the wallet signature
    is_valid = await verify_signature(request.wallet_address, request.signature)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Scrape the article content
    article_content = await scrape_article(str(request.article_url))
    
    # Summarize the content
    summary_content = await summarizer.summarize_text(article_content)
    
    # Store the summary in the database
    repository = SummaryRepository(db)
    summary = await repository.create_summary(
        wallet_address=request.wallet_address,
        article_url=str(request.article_url),
        original_content=article_content,
        summary_content=summary_content
    )
    
    return summary

@router.get("/summaries/{wallet_address}", response_model=SummaryListResponse)
async def get_summaries_by_wallet(
    wallet_address: str,
    db: Session = Depends(get_db)
):
    repository = SummaryRepository(db)
    summaries = await repository.get_summaries_by_wallet(wallet_address)
    
    return SummaryListResponse(summaries=summaries)
