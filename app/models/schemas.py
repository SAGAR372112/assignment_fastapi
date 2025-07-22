from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MarketAnalysisResponse(BaseModel):
    "Response model for market analysis"
    sector: str = Field(..., description="Analyzed sector name")
    analysis_date: str = Field(..., description="ISO format date of analysis")
    markdown_report: str = Field(..., description="Structured markdown analysis report")
    data_sources_count: int = Field(..., description="Number of data sources used")
    user: str = Field(..., description="User who requested the analysis")

class MarketData(BaseModel):
    "Market data structure"
    news: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)