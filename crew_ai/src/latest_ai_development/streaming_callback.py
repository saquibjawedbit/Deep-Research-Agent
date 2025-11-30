"""
Custom callback handler for streaming CrewAI agent activities to the frontend.
"""
import asyncio
from typing import Any, Dict, Optional
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin


class StreamingCallbackHandler:
    """
    Callback handler that captures CrewAI agent and task events
    and streams them to the frontend via an async queue.
    """
    
    def __init__(self, status_queue: asyncio.Queue):
        """
        Initialize the streaming callback handler.
        
        Args:
            status_queue: Async queue to send status updates to
        """
        self.status_queue = status_queue
        self.current_agent = None
        self.current_task = None
        
    async def on_agent_start(self, agent_name: str, task_description: str):
        """Called when an agent starts working on a task."""
        self.current_agent = agent_name
        self.current_task = task_description
        await self.status_queue.put({
            "type": "agent_started",
            "agent": agent_name,
            "message": f"Starting: {task_description[:100]}...",
            "task": task_description
        })
    
    async def on_agent_step(self, step_output: Any):
        """Called after each step an agent takes."""
        try:
            # Extract thought/action from step output
            if hasattr(step_output, 'log'):
                log_text = step_output.log
                
                # Parse the log to extract meaningful information
                if "Thought:" in log_text:
                    thought = log_text.split("Thought:")[1].split("\n")[0].strip()
                    await self.status_queue.put({
                        "type": "thinking",
                        "agent": self.current_agent,
                        "message": thought[:200]
                    })
                
                if "Action:" in log_text:
                    action = log_text.split("Action:")[1].split("\n")[0].strip()
                    await self.status_queue.put({
                        "type": "action",
                        "agent": self.current_agent,
                        "message": f"Taking action: {action[:150]}"
                    })
                    
            elif hasattr(step_output, 'return_values'):
                # Agent finished with output
                output = str(step_output.return_values.get('output', ''))[:200]
                await self.status_queue.put({
                    "type": "step_complete",
                    "agent": self.current_agent,
                    "message": f"Completed step: {output}"
                })
        except Exception as e:
            # Silently handle parsing errors
            pass
    
    async def on_task_start(self, task_name: str, task_description: str):
        """Called when a task starts."""
        await self.status_queue.put({
            "type": "task_started",
            "task": task_name,
            "message": f"Starting task: {task_name}",
            "description": task_description[:150]
        })
    
    async def on_task_complete(self, task_output: Any):
        """Called when a task completes."""
        try:
            output_text = str(task_output.raw)[:200] if hasattr(task_output, 'raw') else str(task_output)[:200]
            await self.status_queue.put({
                "type": "task_completed",
                "task": self.current_task,
                "message": f"Task completed: {output_text}..."
            })
        except Exception:
            await self.status_queue.put({
                "type": "task_completed",
                "task": self.current_task,
                "message": "Task completed successfully"
            })
    
    async def on_tool_start(self, tool_name: str, tool_input: str):
        """Called when a tool is about to be used."""
        await self.status_queue.put({
            "type": "tool_start",
            "agent": self.current_agent,
            "message": f"Using tool: {tool_name}",
            "tool": tool_name,
            "input": tool_input[:100]
        })
    
    async def on_tool_end(self, tool_name: str, tool_output: str):
        """Called when a tool finishes."""
        await self.status_queue.put({
            "type": "tool_end",
            "agent": self.current_agent,
            "message": f"Tool {tool_name} completed",
            "tool": tool_name
        })
    
    async def on_error(self, error: Exception):
        """Called when an error occurs."""
        await self.status_queue.put({
            "type": "error",
            "message": str(error)
        })


def create_step_callback(handler: StreamingCallbackHandler):
    """
    Create a step_callback function for CrewAI agents.
    
    Args:
        handler: The streaming callback handler instance
        
    Returns:
        A callback function that can be passed to CrewAI agents
    """
    def step_callback(step_output):
        """Sync wrapper for async step callback."""
        try:
            # Create event loop if needed
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(handler.on_agent_step(step_output))
            else:
                # If no loop, run it
                loop.run_until_complete(handler.on_agent_step(step_output))
        except Exception:
            pass
    
    return step_callback


def create_task_callback(handler: StreamingCallbackHandler):
    """
    Create a task_callback function for CrewAI tasks.
    
    Args:
        handler: The streaming callback handler instance
        
    Returns:
        A callback function that can be passed to CrewAI tasks
    """
    def task_callback(task_output):
        """Sync wrapper for async task callback."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(handler.on_task_complete(task_output))
            else:
                loop.run_until_complete(handler.on_task_complete(task_output))
        except Exception:
            pass
    
    return task_callback
