from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter # type: ignore
from slowapi.util import get_remote_address # type: ignore
from app.models.schemas import MarketAnalysisResponse
from app.core.auth import AuthManager
from app.services.data_collector import DataCollector
from app.services.ai_analyzer import AIAnalyzer
from datetime import datetime
from typing import Dict, Any
import logging
from app.core.config import Settings
import re

router = APIRouter(tags=["Sector Analysis"])

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

security = HTTPBearer()

settings = Settings()

auth_manager = AuthManager(settings)

data_collector = DataCollector()

ai_analyzer = AIAnalyzer(settings.gemini_api_key)

active_sessions: Dict[str, Dict[str, Any]] = {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    "Validate JWT token and get current user"
    try:
        payload = auth_manager.verify_token(credentials.credentials)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update session
        if username in active_sessions:
            active_sessions[username]["last_activity"] = datetime.utcnow()
            active_sessions[username]["request_count"] = active_sessions[username].get("request_count", 0) + 1
        
        return username
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/analyze/{sector}", response_model=MarketAnalysisResponse)
@limiter.limit("5/minute;30/day")
async def analyze_sector(
    request: Request,
    sector: str,
    current_user: str = Depends(get_current_user)
):
    """
    Analyze trade opportunities for a specific sector in India
    
    - sector: Name of the sector (e.g., pharmaceuticals, technology, agriculture)
    - Returns: Structured markdown report with market analysis
    """
    try:
        logger.info(f"Starting analysis for sector: {sector} by user: {current_user}")
        
        # Validate sector input
        sector = re.sub(r'[^a-zA-Z\s]', '', sector.strip().lower())
        if not sector or len(sector) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sector name. Must be at least 2 characters long."
            )
        
        # Check session limits for guests
        if current_user in active_sessions:
            session = active_sessions[current_user]
            if session.get("is_guest") and session.get("request_count", 0) >= 5:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Guest user request limit exceeded. Please login for more requests."
                )
        
        # Step 1: Collect market data
        logger.info(f"Collecting market data for {sector}")
        market_data = await data_collector.collect_sector_data(sector)
        
        if not market_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No market data found for sector: {sector}"
            )
        
        # Step 2: AI Analysis
        logger.info(f"Analyzing data with AI for {sector}")
        analysis_report = await ai_analyzer.analyze_market_data(sector, market_data)
        
        # Step 3: Generate response
        response = MarketAnalysisResponse(
            sector=sector.title(),
            analysis_date=datetime.utcnow().isoformat(),
            markdown_report=analysis_report,
            data_sources_count=len(market_data.get('sources', [])),
            user=current_user
        )
        
        logger.info(f"Analysis completed successfully for {sector}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error for {sector}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sector: {sector}. Please try again later."
        )