import operator
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from models.schema import SearchQuery, Section
from search.client import TavilySearch
from typing_extensions import TypedDict


class ReportStateInput(TypedDict):
    topic: str


class ReportStateOutput(TypedDict):
    final_report: str


class ReportState(TypedDict):
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[list, operator.add]
    report_sections_from_research: str  # string of any completed sections from research to write final sections
    final_report: str  # final report


class SectionState(TypedDict):
    section: Section  # Report section
    search_queries: list[SearchQuery]  # list of search queries
    source_str: str  # string of formatted source content from web search
    report_sections_from_research: str  # string of any completed sections from research to write final sections
    completed_sections: list[
        Section
    ]  # final key we duplicate in outer state for Send() API


class SectionOutputState(TypedDict):
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API


class SectionStateInput(TypedDict):
    section: Section  # Report section
    llm_client: ChatAnthropic
    search_client: TavilySearch
