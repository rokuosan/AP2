# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides a FunctionCallResolver class.

The FunctionCallResolver uses a LLM to determine which tool to
use based on the instructions provided.
"""

import logging

from collections.abc import Callable
from typing import Any

from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import Task
from common.model_config import model_name, vllm_client, vllm_enabled
from google import genai
from google.genai import types


DataPartContent = dict[str, Any]
Tool = Callable[[list[DataPartContent], TaskUpdater, Task | None], Any]


class FunctionCallResolver:
  """Resolves a natural language prompt to the name of a tool."""

  def __init__(
      self,
      tools: list[Tool],
      instructions: str = "You are a helpful assistant.",
  ):
    """Initialization.

    Args:
      tools: The list of tools that a request can be resolved to.
      instructions: The instructions to guide the LLM.
    """
    self._tools = tools
    self._instructions = instructions
    self._client = None if vllm_enabled() else genai.Client()
    function_declarations = [
        types.FunctionDeclaration(
            name=tool.__name__, description=tool.__doc__
        )
        for tool in tools
    ]
    self._config = types.GenerateContentConfig(
        system_instruction=instructions,
        tools=[types.Tool(function_declarations=function_declarations)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        # Force the model to call 'any' function, instead of chatting.
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="ANY")
        ),
    )

  async def determine_tool_to_use(self, prompt: str) -> str:
    """Determines which tool to use based on a user's prompt.

    Uses a LLM to analyze the user's prompt and decide which of the available
    tools (functions) is the most appropriate to handle the request.

    Args:
        prompt: The user's request as a string.

    Returns:
        The name of the tool function that the model has determined should be
        called. If no suitable tool is found, it returns "Unknown".
    """
    if self._client is None:
      async with vllm_client() as client:
        completion = await client.chat.completions.create(
            model=model_name(),
            messages=[
                {"role": "system", "content": self._instructions},
                {"role": "user", "content": prompt},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": tool.__name__,
                        "description": tool.__doc__ or "",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
                for tool in self._tools
            ],
            tool_choice="required",
        )
      calls = completion.choices[0].message.tool_calls
      return calls[0].function.name if calls else "Unknown"

    response = await self._client.aio.models.generate_content(
        model=model_name(),
        contents=prompt,
        config=self._config,
    )

    logging.debug("\nDetermine Tool Response: %s\n", response)

    if (
        response.candidates
        and response.candidates[0].content
        and response.candidates[0].content.parts
    ):
      for part in response.candidates[0].content.parts:
        if part.function_call:
          return part.function_call.name

    return "Unknown"
