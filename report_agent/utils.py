from models.schema import Section


def _convert_search_results(search_response) -> list:
    # Convert input to list of results
    if isinstance(search_response, dict):
        sources_list = search_response["results"]
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            if isinstance(response, dict) and "results" in response:
                sources_list.extend(response["results"])
            else:
                sources_list.extend(response)
    else:
        raise ValueError(
            "input must be either a dict with 'results' or a list of search results"
        )

    return sources_list


def _format_source_output(
    unique_sources: dict[str, dict[str, str]],
    max_tokens_per_source: int,
    include_raw_content: bool,
) -> str:
    formatted_text = "Sources:\n\n"

    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source["title"]}:\n===\n"
        formatted_text += f"URL: {source["url"]}\n===\n"
        formatted_text += (
            f"Most relevant content from source: {source["content"]}\n===\n"
        )

        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4

            # Handle None raw_content
            raw_content = source.get("raw_content", "")
            if raw_content is None:
                raw_content = ""
                print(
                    f"Warning: No raw content found for source {source['url']}"
                )

            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "...[truncated]"

            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"

    return formatted_text.strip()


def deduplicate_and_format_sources(
    search_response, max_tokens_per_source: int, include_raw_content=True
) -> str:
    """
    Takes either a single search response or list of responses from Tavily API and formats them.
    Limits the raw_content to approximately max_tokens_per_source.
    include_raw_content specifies whether to include the raw_content from Tavily in the formatted string.

    Args:
        search_response: Either:
            - A dict with a 'results' key containing a list of search results
            - A list of dicts, each containing search results

    Returns:
        str: Formatted string with deduplicated sources
    """
    # Convert input to list of results
    sources_list = _convert_search_results(search_response)

    # Deduplicate by URL
    unique_sources = {}
    for source in sources_list:
        if source["url"] not in unique_sources:
            unique_sources[source["url"]] = source

    formatted_text = _format_source_output(
        unique_sources=unique_sources,
        max_tokens_per_source=max_tokens_per_source,
        include_raw_content=include_raw_content,
    )

    return formatted_text


def format_sections(sections: list[Section]) -> str:
    """Format a list of sections into a string"""
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'='*60}
Section {idx}: {section.name}
{'='*60}
Description:
{section.description}
Requires Research:
{section.research}

Content:
{section.content if section.content else '[Not yet written]'}

"""
    return formatted_str