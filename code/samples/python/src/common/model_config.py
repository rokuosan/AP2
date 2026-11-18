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

"""Model configuration shared by the Python demos."""

import os

from google.adk.models.base_llm import BaseLlm
from openai import AsyncOpenAI


def model_name() -> str:
  return os.environ.get("AGENT_MODEL", "gemini-3.1-flash-lite-preview")


def vllm_enabled() -> bool:
  return bool(os.environ.get("VLLM_BASE_URL"))


def _vllm_options() -> dict[str, str]:
  if not os.environ.get("AGENT_MODEL"):
    raise ValueError("Set AGENT_MODEL to the model served by vLLM.")
  return {
      "base_url": os.environ["VLLM_BASE_URL"].rstrip("/"),
      "api_key": os.environ.get("VLLM_API_KEY") or "EMPTY",
  }


def agent_model() -> str | BaseLlm:
  if not vllm_enabled():
    return model_name()

  from google.adk.models.lite_llm import LiteLlm

  options = _vllm_options()
  return LiteLlm(
      model=f"openai/{model_name()}",
      api_base=options["base_url"],
      api_key=options["api_key"],
  )


def vllm_client() -> AsyncOpenAI:
  return AsyncOpenAI(**_vllm_options())
