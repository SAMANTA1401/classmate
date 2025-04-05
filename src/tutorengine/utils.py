from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import BaseMessage
import operator
from pydantic import BaseModel, Field
from typing import Optional
from langchain.output_parsers import PydanticOutputParser


class BaseMessage:
    def __init__(self, content: str):
        self.content = content

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

#parser for master bot
class FieldSelectionParser(BaseModel):
    Field_study: Optional[str] = Field(default=None, description='Selected fields (science, arts, or N/A)')
    Subject: Optional[str] = Field(default=None, description='Selected subjects')
    Chapter: Optional[str] = Field(default=None, description='Selected chapters')
    Topic: Optional[str] = Field(default=None, description='Selected topic')
    Difficulty_level: Optional[str] = Field(default=None, description='Selected difficulty level')
    Question_or_query: Optional[str] = Field(default=None, description='Given input question or query')
    Answer: Optional[str] = Field(default=None, description='Answer to the given question or query')
    Content: Optional[str] = Field(default=None, description='Content of the selected topic')
    
# parser for search tools
class SearchAnswer(BaseModel):
    extracted_result:str = Field(description="A concise answer to the user's query extracted from context")