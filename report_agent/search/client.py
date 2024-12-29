import asyncio

from langsmith import traceable
from models.schema import SearchQuery
from tavily import AsyncTavilyClient


class TavilySearch:
    def __init__(self, client: AsyncTavilyClient) -> None:
        self.client = client

    @traceable
    async def tavily_search_async(
        self,
        search_queries: list[SearchQuery],
        tavily_topic: str,
        tavily_days: int,
    ) -> list[dict]:
        """
        Performs concurrent web searches using the Tavily API.

        Args:
            search_queries (List[SearchQuery]): List of search queries to process
            tavily_topic (str): Type of search to perform ('news' or 'general')
            tavily_days (int): Number of days to look back for news articles (only used when tavily_topic='news')

        Returns:
            List[dict]: List of search results from Tavily API, one per query

        Note:
            For news searches, each result will include articles from the last `tavily_days` days.
            For general searches, the time range is unrestricted.
        """
        search_tasks = []
        for query in search_queries:
            if tavily_topic == "news":
                search_tasks.append(
                    self.client.search(
                        query.search_query,
                        max_results=5,
                        include_raw_content=True,
                        topic="news",
                        days=tavily_days,
                    )
                )
            else:
                search_tasks.append(
                    self.client.search(
                        query.search_query,
                        max_results=5,
                        include_raw_content=True,
                        topic="general",
                    )
                )

        # Execute all searches concurrently
        search_docs = await asyncio.gather(*search_tasks)

        return search_docs
