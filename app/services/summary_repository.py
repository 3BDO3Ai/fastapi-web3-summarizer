from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.future import select
from fastapi import Depends
from typing import List, Optional

from .. import models
from ..database import get_db

class SummaryRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_summary(
        self,
        wallet_address: str,
        article_url: str,
        original_content: str,
        summary_content: str
    ) -> models.Summary:
        """
        Create a new summary in the database
        
        Args:
            wallet_address: The wallet address of the user
            article_url: The URL of the article
            original_content: The original content of the article
            summary_content: The summarized content
            
        Returns:
            models.Summary: The created summary object
        """
        db_summary = models.Summary(
            wallet_address=wallet_address,
            article_url=article_url,
            original_content=original_content,
            summary_content=summary_content
        )
        self.db.add(db_summary)
        await self.db.commit()
        await self.db.refresh(db_summary)
        return db_summary
    
    async def get_summaries_by_wallet(self, wallet_address: str) -> List[models.Summary]:
        """
        Get all summaries for a specific wallet address
        
        Args:
            wallet_address: The wallet address to filter by
            
        Returns:
            List[models.Summary]: List of summary objects
        """
        query = select(models.Summary).where(
            models.Summary.wallet_address == wallet_address
        ).order_by(desc(models.Summary.created_at))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_summary_by_id(self, summary_id: int) -> Optional[models.Summary]:
        """
        Get a summary by its ID
        
        Args:
            summary_id: The ID of the summary to retrieve
            
        Returns:
            Optional[models.Summary]: The summary object if found, None otherwise
        """
        query = select(models.Summary).where(models.Summary.id == summary_id)
        result = await self.db.execute(query)
        return result.scalars().first()
