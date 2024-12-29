import os
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send
from models.dependencies import Dependencies
from models.schema import Section
from models.states import ReportState, SectionState
from prompts import FINAL_SECTION_WRITER_INSTRUCTIONS
from typing_extensions import cast
from utils import format_sections


class ReportNode:
    def __init__(self, deps: Dependencies):
        self.deps = deps

    def initiate_section_writing(self, state: ReportState) -> list:
        """This is the "map" step to kick off web research for some sections of the report"""
        # Kick off section writing in parallel via Send() API for any sections that require research
        return [
            Send("build_section_with_web_research", {"section": s})
            for s in state["sections"]
            if s.research
        ]

    async def write_final_sections(self, state: SectionState):
        """Write final sections of report, which do not require web search and use the completed sections as context"""
        # Get state
        section = state["section"]
        completed_report_sections = state["report_sections_from_research"]
        claude_3_5_sonnet = self.deps.llm_client

        # Format system instructions
        system_instructions = FINAL_SECTION_WRITER_INSTRUCTIONS.format(
            section_title=section.name,
            section_topic=section.description,
            context=completed_report_sections,
        )

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

        structured_content = cast(Section, section_content)

        # Write content to section
        section.content = structured_content.content

        # Write the updated section to completed section
        return {"completed_sections": [section]}

    def gather_completed_sections(self, state: ReportState):
        """Gather completed sections from research and format them as context for writing the final sections"""

        # List completed sections
        completed_sections = state["completed_sections"]

        # Format completed section to stri to use as context for final sections
        completed_report_sections = format_sections(completed_sections)

        return {"report_sections_from_research": completed_report_sections}

    def initiate_final_section_writing(self, state: ReportState) -> list:
        """Write any final sections using the Send() API to parallelise the process"""
        return [
            Send(
                "write_final_sections",
                {
                    "section": s,
                    "report_sections_from_research": state[
                        "report_sections_from_research"
                    ],
                },
            )
            for s in state["sections"]
            if not s.research
        ]

    def compile_final_report(self, state: ReportState):
        """Compile the final report"""
        # Get sections
        sections = state["sections"]
        completed_sections = {
            s.name: s.content for s in state["completed_sections"]
        }

        # Update sections with completed content while maintaining original order
        for section in sections:
            section.content = completed_sections[section.name]

        # Compile final report
        all_sections = "\n\n".join([s.content for s in sections])

        return {"final_report": all_sections}

    def save_final_report(self, state: ReportState):
        """Save markdown file"""
        # Get the final report content from state
        final_report = state["final_report"]

        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/report_{timestamp}.md"

        # Write content to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_report)

        print(f"Report saved to: {filename}")

        # Return unchanged state
        return state
