# ruff: noqa
# Copyright 2026 Google LLC
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

import datetime
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.image_tool import generate_dish_image
from app.online_recipe_tool import fetch_online_recipes
from app.pantry_tools import (
    add_or_update_pantry_item,
    get_pantry_items,
    remove_pantry_item,
)
from app.recipe_tools import search_recipes
from app.video_tool import generate_dish_video

AGENT_ENGINE_RESOURCE_NAME = "projects/285881095630/locations/us-east1/reasoningEngines/4081204643374301184"

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_prompt = schema_manager.generate_system_prompt(
    role_description=(
        "You are the Smart Culinary & Recipe Coach. You help home cooks plan meals, "
        "optimize pantry usage, and discover recipes tailored to their dietary preferences "
        "and available ingredients."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        f"{a2ui_prompt}\n\n"
        "ADDITIONAL AGENT INSTRUCTIONS:\n"
        "CODE EXECUTION:\n"
        "You have access to a secure Python code execution sandbox. Use Python code execution for "
        "calculating scaled ingredient amounts, unit conversions, or recipe ratio adjustments.\n\n"
        "IMAGE & VIDEO GENERATION TOOLS:\n"
        "- generate_dish_image: Generate high-resolution food presentation images for recommended dishes.\n"
        "- generate_dish_video: Generate short video clips for recommended dishes or cooking techniques using Google Omni model.\n\n"
        "RECIPE SEARCH TOOLS:\n"
        "- search_recipes: Search internal recipe catalog matching available ingredients, max prep time, and dietary restrictions.\n"
        "- fetch_online_recipes: Fetch real-world online recipes, ingredients, and instructions from TheMealDB public API.\n\n"
        "PANTRY INVENTORY TOOLS:\n"
        "You have access to Firestore database tools for managing pantry inventory:\n"
        "- get_pantry_items: Query the active Firestore pantry inventory (optionally filter by category).\n"
        "- add_or_update_pantry_item: Add new ingredients or update quantities in Firestore.\n"
        "- remove_pantry_item: Delete ingredients when they are used up.\n\n"
        "ALLERGY & DIETARY MEMORY RULES:\n"
        "1. You must carefully remember and strictly enforce ALL user food allergies (e.g. peanuts, tree nuts, "
        "dairy/lactose, shellfish, eggs, wheat/gluten, soy, sesame, fish), food intolerances, and dietary restrictions "
        "(e.g. vegan, vegetarian, halal, kosher, low-sodium) disclosed in any session.\n"
        "2. Preload and review the user's preloaded memories at the beginning of every interaction.\n"
        "3. NEVER suggest recipes, ingredients, or meal ideas that contain any allergen or restricted ingredient "
        "disclosed by the user unless explicitly requested for someone else."
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME
    ),
    tools=[
        PreloadMemoryTool(),
        generate_dish_image,
        generate_dish_video,
        search_recipes,
        fetch_online_recipes,
        get_pantry_items,
        add_or_update_pantry_item,
        remove_pantry_item,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
