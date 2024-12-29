# Create a dependency container
from langchain_anthropic.chat_models import ChatAnthropic
from search.client import TavilySearch
from tavily import AsyncTavilyClient


class Dependencies:
    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20240620",
        model_timeout: int = 100,
    ):
        self.llm_client = ChatAnthropic(
            model_name=model_name,
            timeout=model_timeout,
            stop=None,
        )
        self.search_client = TavilySearch(client=AsyncTavilyClient())
