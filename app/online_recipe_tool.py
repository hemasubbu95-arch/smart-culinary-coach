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

import json
import os
import urllib.parse
import urllib.request


def fetch_online_recipes(query: str) -> str:
    """Fetches real-time online recipes and cooking instructions from TheMealDB API.

    Args:
        query: Ingredient or dish name to search for (e.g. 'chicken', 'pasta', 'curry').

    Returns:
        Formatted string containing matching real-world recipes, ingredients, and instructions.
    """
    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartCulinaryCoach/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return f"Error fetching recipes from online API (Status {response.status})."

            payload = json.loads(response.read().decode("utf-8"))
            meals = payload.get("meals")

            if not meals:
                return f"No online recipes found for query: '{query}'."

            formatted_recipes = []
            for meal in meals[:3]:  # Top 3 matches
                title = meal.get("strMeal", "Unknown Meal")
                category = meal.get("strCategory", "General")
                area = meal.get("strArea", "International")
                instructions = meal.get("strInstructions", "No instructions provided.").strip()

                # Extract ingredients & measurements
                ingredients_list = []
                for i in range(1, 21):
                    ing = meal.get(f"strIngredient{i}")
                    meas = meal.get(f"strMeasure{i}")
                    if ing and ing.strip():
                        item_str = f"{meas.strip()} {ing.strip()}".strip() if meas else ing.strip()
                        ingredients_list.append(item_str)

                recipe_entry = (
                    f"🍽️ **{title}** ({category} | {area} Cuisine)\n"
                    f"- Ingredients: {', '.join(ingredients_list)}\n"
                    f"- Instructions:\n{instructions}"
                )
                formatted_recipes.append(recipe_entry)

            return "\n\n---\n\n".join(formatted_recipes)

    except Exception as e:
        return f"Failed to connect to online recipe service: {e}"
