# Multi-Agent Research Assistant

## Overview
This repository contains a sophisticated multi-agent system designed to automatically generate comprehensive research reports on any given topic.
The system leverages LangGraph for orchestration, Anthropic's Claude API for natural language processing, and Tavily's search API for web research.

## Key Features
- Automated report generation with multiple specialized agents
- Parallel processing of research tasks
- Web search integration for up-to-date information
- Structured report formatting with Markdown
- Configurable report structure and research parameters
- Automatic source citation and deduplication

## Architecture

### Core Components

1. **Report Agent**
   - Manages the overall report generation process
   - Orchestrates section writing and compilation
   - Handles final report assembly and saving

2. **Section Agent**
   - Generates search queries for specific topics
   - Processes web search results
   - Writes individual report sections

3. **Search Integration**
   - Uses Tavily API for web searches
   - Supports both general and news-specific searches
   - Implements concurrent search processing

### State Management

The system uses TypedDict classes to manage different states:
- `ReportState`: Overall report state
- `SectionState`: Individual section states
- `ReportStateInput`: Input configuration
- `ReportStateOutput`: Final report output

## Setup

1. Install dependencies:
```bash
make install
```

2. Set up environment variables:
```bash
ANTHROPIC_API_KEY=your_anthropic_key
TAVILY_API_KEY=your_tavily_key
```

3. Optional configuration:
```python
report_structure = "custom_structure"
number_of_queries = 3
tavily_topic = "news"
tavily_days = 7
```

## Report Structure

Default report structure includes:
1. Introduction
2. Main Body Sections (research-based)
3. Conclusion with summary elements

Each section contains:
- Title
- Description
- Research flag
- Content
- Source citations (where applicable)

## Output

Reports are saved as Markdown files with:
- Structured sections
- Formatted content
- Source citations
- Tables and lists where appropriate
- Timestamps in filenames
