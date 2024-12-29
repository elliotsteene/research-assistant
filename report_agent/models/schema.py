from pydantic import BaseModel, Field


class Section(BaseModel):
    name: str = Field(description="Name of this section of the report")
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section."
    )
    research: bool = Field(
        description="Whether to perform web research for this section of the report"
    )
    content: str = Field(description="The content of the section")


class Sections(BaseModel):
    sections: list[Section] = Field(description="Sections of the report")


class SearchQuery(BaseModel):
    search_query: str = Field("", description="Query for web search")


class Queries(BaseModel):
    queries: list[SearchQuery] = Field(description="List of search queries")
