"""Base classes for custom tools in the Deep Research Crew system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ResearchToolInput(BaseModel):
    """Base input schema for research tools."""
    pass


class ResearchToolOutput(BaseModel):
    """Base output schema for research tools."""
    success: bool = Field(description="Whether the tool execution was successful")
    message: str = Field(description="Human-readable message about the result")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Tool-specific output data")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")


class BaseResearchTool(BaseTool, ABC):
    """
    Base class for all Deep Research Crew tools.
    
    Provides common functionality like error handling, logging, and output formatting.
    """
    
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    args_schema: Type[BaseModel] = Field(default=ResearchToolInput)
    
    def _run(self, **kwargs: Any) -> ResearchToolOutput:
        """
        Execute the tool with error handling.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            ResearchToolOutput with results or error information
        """
        try:
            result = self.execute(**kwargs)
            return ResearchToolOutput(
                success=True,
                message=f"{self.name} completed successfully",
                data=result
            )
        except Exception as e:
            return ResearchToolOutput(
                success=False,
                message=f"{self.name} failed",
                error=str(e)
            )
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool's core logic.
        
        Must be implemented by subclasses.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary containing tool results
        """
        pass
