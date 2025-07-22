import asyncio
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import logging
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataCollector:
    "Collect market data from various sources."

    def __init__(self):
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
        }

    async def collect_sector_data(self, sector: str) -> Dict[str, Any]:
        "Collect data for a specific sector using concurrent tasks."
        try:
            market_data = {
                'news': [],
                'sources': [],
                'sector_info': {},
                'timestamp': datetime.utcnow().isoformat()
            }

            # Concurrently gather news and sector info
            news_data, sector_info = await asyncio.gather(
                self._search_news(sector),
                self._get_sector_info(sector)
            )

            market_data['news'] = news_data
            market_data['sector_info'] = sector_info
            market_data['sources'] = [
                "DuckDuckGo News Search",
                "Economic Times India",
                "Business Standard"
            ]

            logger.info(f"[{sector}] Collected {len(news_data)} news articles.")
            return market_data

        except Exception as e:
            logger.exception(f"Error collecting sector data for '{sector}': {e}")
            return {}

    async def _search_news(self, sector: str) -> List[Dict[str, Any]]:
        "Search for recent news articles using DuckDuckGo (via requests in a thread)."

        def fetch_news() -> List[Dict[str, Any]]:
            try:
                query = quote_plus(f"{sector} sector news site:economictimes.indiatimes.com OR site:business-standard.com")
                url = f"https://html.duckduckgo.com/html/?q={query}"
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all("a", class_="result__a")

                news_items = []
                for i, tag in enumerate(results[:8]):  # Increased count for variety
                    title = tag.get_text(strip=True)
                    link = tag.get('href')

                    # Skip sponsored or unrelated ads
                    if "duckduckgo.com/y.js" in link or "bing.com" in link:
                        continue

                    snippet = tag.find_parent("div", class_="result__body")
                    summary = ""
                    if snippet:
                        snippet_tag = snippet.find("a", class_="result__snippet")
                        if snippet_tag:
                            summary = snippet_tag.get_text(strip=True)

                    news_items.append({
                        'title': title,
                        'summary': summary or "No summary available.",
                        'url': link,
                        'relevance': round(1 - i * 0.1, 2)
                    })

                return news_items

            except Exception as e:
                logger.error(f"Error fetching news for '{sector}': {e}")
                return []

        return await asyncio.to_thread(fetch_news)

    async def _get_sector_info(self, sector: str) -> Dict[str, Any]:
        "Simulate additional sector insights (can be replaced by live API/scraping)."
        await asyncio.sleep(0)  # Simulate I/O delay
        return {
            'sector_name': sector.title(),
            'market_size': 'Estimated $10B (2025 forecast)',
            'growth_rate': '6.2% CAGR',
            'key_players': ['Company A', 'Company B', 'Company C'],
            'government_policies': 'PLI Scheme, FDI norms eased'
        }
