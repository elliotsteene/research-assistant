from typing import cast

from config.configuration import Configuration
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from models.dependencies import Dependencies
from models.schema import Queries, Section, Sections
from models.states import ReportState, SectionState
from prompts import (
    QUERY_WRITER_INSTRUCTIONS,
    REPORT_PLANNER_INSTRUCTIONS,
    REPORT_PLANNER_QUERY_WRITER_INSTRUCTIONS,
    SECTION_WRITER_INSTRUCTIONS,
)
from utils import deduplicate_and_format_sources


class SectionNode:
    def __init__(self, deps: Dependencies):
        self.deps = deps

    async def generate_report_plan(
        self, state: ReportState, config: RunnableConfig
    ):
        """Generate the report plan"""

        # Input
        topic = state["topic"]
        claude_3_5_sonnet = self.deps.llm_client
        tavily_client = self.deps.search_client

        # Get configuration
        configurable = Configuration.from_runnable_config(config)
        report_structure = configurable.report_structure
        number_of_queries = configurable.number_of_queries
        tavily_topic = configurable.tavily_topic
        tavily_days = configurable.tavily_days

        # Convert JSON object to string if necessary
        if isinstance(report_structure, dict):
            report_structure = str(report_structure)

        # Generate search query
        structured_llm = claude_3_5_sonnet.with_structured_output(Queries)

        # Format system instructions
        system_instructions_query = (
            REPORT_PLANNER_QUERY_WRITER_INSTRUCTIONS.format(
                topic=topic,
                report_organization=report_structure,
                number_of_queries=number_of_queries,
            )
        )

        # Generate queries
        results = await structured_llm.ainvoke(
            [SystemMessage(content=system_instructions_query)]
            + [
                HumanMessage(
                    content="Generate search queries that will help with planning the sections of the report"
                )
            ]
        )
        structured_results = cast(Queries, results)

        # Web search
        # query_list = [query for query in structured_results.queries]

        # Search web
        search_docs = await tavily_client.tavily_search_async(
            search_queries=structured_results.queries,
            tavily_topic=tavily_topic,
            tavily_days=tavily_days,
        )

        # Deduplicate and format sources
        source_str = deduplicate_and_format_sources(
            search_docs, max_tokens_per_source=1000, include_raw_content=False
        )

        # Format system instructions
        system_instructions_sections = REPORT_PLANNER_INSTRUCTIONS.format(
            topic=topic,
            report_organization=report_structure,
            context=source_str,
        )

        # Generate sections
        section_structured_llm = claude_3_5_sonnet.with_structured_output(
            Sections
        )
        report_sections = await section_structured_llm.ainvoke(
            [SystemMessage(content=system_instructions_sections)]
            + [
                HumanMessage(
                    content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields."
                )
            ]
        )

        structured_report_sections = cast(Sections, report_sections)

        return {"sections": structured_report_sections.sections}

    async def generate_queries(
        self, state: SectionState, config: RunnableConfig
    ):
        """Generate search queries for a report section"""

        # Get section
        section = state["section"]
        claude_3_5_sonnet = self.deps.llm_client

        # Get configuration
        configurable = Configuration.from_runnable_config(config)
        number_of_queries = configurable.number_of_queries

        # Generate queries
        structured_llm = claude_3_5_sonnet.with_structured_output(Queries)

        # Format system instructions
        system_instructions = QUERY_WRITER_INSTRUCTIONS.format(
            section_topic=section.description,
            number_of_queries=number_of_queries,
        )

        # Generate queries
        queries = await structured_llm.ainvoke(
            [SystemMessage(content=system_instructions)]
            + [
                HumanMessage(
                    content="Generate search queries on the provided topic."
                )
            ]
        )

        structured_queries = cast(Queries, queries)

        return {"search_queries": structured_queries.queries}

    async def search_web(self, state: SectionState, config: RunnableConfig):
        """Search the web for each query, then return a list of raw sources and a formatted string of sources"""

        # Get state
        search_queries = state["search_queries"]
        tavily_client = self.deps.search_client

        # Get configuration
        configurable = Configuration.from_runnable_config(config)
        tavily_topic = configurable.tavily_topic
        tavily_days = configurable.tavily_days

        # Web search
        # query_list = [query.search_query for query in search_queries]
        search_docs = await tavily_client.tavily_search_async(
            search_queries, tavily_topic, tavily_days
        )

        # Deduplicate and formate sources
        source_str = deduplicate_and_format_sources(
            search_docs, max_tokens_per_source=5000, include_raw_content=True
        )

        return {"source_str": source_str}

    async def write_section(self, state: SectionState):
        """Write a section of the report"""

        # Get state
        section = state["section"]
        source_str = state["source_str"]
        claude_3_5_sonnet = self.deps.llm_client

        # Format system instructions
        system_instructions = SECTION_WRITER_INSTRUCTIONS.format(
            section_title=section.name,
            section_topic=section.description,
            context=source_str,
        )

        # Generate queries
        structured_llm = claude_3_5_sonnet.with_structured_output(Section)

        # Generate section
        section_content = await structured_llm.ainvoke(
            [SystemMessage(content=system_instructions)]
            + [
                HumanMessage(
                    content="Generate a report section based on the provided sources."
                )
            ]
        )

        structured_section = cast(Section, section_content)

        # Write content to the section object
        section.content = structured_section.content

        # Write the updated section to the completed sections
        return {"completed_sections": [section]}
