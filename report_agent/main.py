import asyncio

from config.configuration import Configuration
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from models.dependencies import Dependencies
from models.states import (
    ReportState,
    ReportStateInput,
    ReportStateOutput,
    SectionOutputState,
    SectionState,
    SectionStateInput,
)
from nodes.report import ReportNode
from nodes.section import SectionNode


def build_section_graph(deps: Dependencies) -> StateGraph:
    section_builder = StateGraph(
        SectionState,
        input=SectionStateInput,
        output=SectionOutputState,
    )

    section_nodes = SectionNode(deps=deps)

    section_builder.add_node("generate_queries", section_nodes.generate_queries)
    section_builder.add_node("search_web", section_nodes.search_web)
    section_builder.add_node("write_section", section_nodes.write_section)

    section_builder.add_edge(START, "generate_queries")
    section_builder.add_edge("generate_queries", "search_web")
    section_builder.add_edge("search_web", "write_section")
    section_builder.add_edge("write_section", END)

    return section_builder


def build_report_graph(
    section_graph: StateGraph, deps: Dependencies
) -> StateGraph:
    report_builder = StateGraph(
        ReportState,
        input=ReportStateInput,
        output=ReportStateOutput,
        config_schema=Configuration,
    )

    report_nodes = ReportNode(deps=deps)
    section_nodes = SectionNode(deps=deps)

    report_builder.add_node(
        "generate_report_plan", section_nodes.generate_report_plan
    )
    report_builder.add_node(
        "build_section_with_web_research", section_graph.compile()
    )
    report_builder.add_node(
        "gather_completed_sections", report_nodes.gather_completed_sections
    )
    report_builder.add_node(
        "write_final_sections", report_nodes.write_final_sections
    )
    report_builder.add_node(
        "compile_final_report", report_nodes.compile_final_report
    )
    report_builder.add_node("save_final_report", report_nodes.save_final_report)

    report_builder.add_edge(START, "generate_report_plan")
    report_builder.add_conditional_edges(
        "generate_report_plan",
        report_nodes.initiate_section_writing,
        ["build_section_with_web_research"],
    )
    report_builder.add_edge(
        "build_section_with_web_research", "gather_completed_sections"
    )
    report_builder.add_conditional_edges(
        "gather_completed_sections",
        report_nodes.initiate_final_section_writing,
        ["write_final_sections"],
    )
    report_builder.add_edge("write_final_sections", "compile_final_report")
    report_builder.add_edge("compile_final_report", "save_final_report")
    report_builder.add_edge("save_final_report", END)

    return report_builder


async def run_model() -> None:
    deps = Dependencies(model_name="claude-3-5-sonnet-20241022")
    section_graph = build_section_graph(deps=deps)
    report_graph = build_report_graph(section_graph=section_graph, deps=deps)

    graph = report_graph.compile()

    # input = ReportStateInput(
    #     topic="Write a detailed report on the current state of UK political parties, their policies and popularity"
    # )
    # input = ReportStateInput(
    #     topic="Generate a comprehensive report on the role and responsibilities of a Principal Designer under UK construction regulations. Explain how this could impact architecture fees"
    # )

    input = ReportStateInput(
        topic="Generate a detailed report on Enzo Maresca's tactics at Chelsea."
    )
    async for event in graph.astream_events(input, version="v1"):
        kind = event["event"]
        print(f"{kind}: {event['name']}")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(run_model())
