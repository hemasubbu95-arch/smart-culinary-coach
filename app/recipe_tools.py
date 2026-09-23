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

RECIPE_CATALOG = [
    {
        "id": "mediterranean_chicken_rice_bowl",
        "title": "Mediterranean Chicken & Rice Bowl",
        "prep_time_minutes": 25,
        "servings": 2,
        "dietary_tags": ["Gluten-Free", "Nut-Free", "Shellfish-Free"],
        "ingredients": [
            "Chicken Breast",
            "Jasmine Rice",
            "Vine Tomatoes",
            "Garlic Cloves",
            "Feta Cheese",
            "Extra Virgin Olive Oil",
        ],
        "instructions": (
            "1. Cook jasmine rice according to package directions.\n"
            "2. Season chicken breast with minced garlic, olive oil, salt, and pepper.\n"
            "3. Pan-sear chicken for 12-15 minutes until fully cooked, then slice.\n"
            "4. Assemble bowl: rice base topped with chicken, diced tomatoes, and crumbled feta cheese."
        ),
    },
    {
        "id": "garlic_chicken_broccoli_stir_fry",
        "title": "Garlic Chicken & Broccoli Stir-Fry",
        "prep_time_minutes": 20,
        "servings": 2,
        "dietary_tags": ["Gluten-Free", "Dairy-Free", "Nut-Free", "Shellfish-Free"],
        "ingredients": [
            "Chicken Breast",
            "Broccoli Florets",
            "Garlic Cloves",
            "Extra Virgin Olive Oil",
        ],
        "instructions": (
            "1. Slice chicken breast into thin strips.\n"
            "2. Heat olive oil in a skillet over medium-high heat and sauté minced garlic for 1 minute.\n"
            "3. Add chicken strips and cook until golden brown (6-8 minutes).\n"
            "4. Toss in broccoli florets, add 2 tbsp water, cover and steam for 4 minutes until tender-crisp."
        ),
    },
    {
        "id": "greek_tomato_feta_salad",
        "title": "Greek Tomato & Feta Salad with Broccoli",
        "prep_time_minutes": 15,
        "servings": 2,
        "dietary_tags": ["Gluten-Free", "Vegetarian", "Nut-Free", "Shellfish-Free"],
        "ingredients": [
            "Vine Tomatoes",
            "Feta Cheese",
            "Broccoli Florets",
            "Extra Virgin Olive Oil",
            "Garlic Cloves",
        ],
        "instructions": (
            "1. Blanch broccoli florets in boiling water for 2 minutes, then drain and cool.\n"
            "2. Dice vine tomatoes and toss with blanched broccoli.\n"
            "3. Whisk olive oil and minced garlic, pour over salad, and top with crumbled feta cheese."
        ),
    },
    {
        "id": "creamy_garlic_rice",
        "title": "Creamy Garlic Jasmine Rice",
        "prep_time_minutes": 35,
        "servings": 4,
        "dietary_tags": ["Gluten-Free", "Vegetarian", "Nut-Free"],
        "ingredients": [
            "Jasmine Rice",
            "Garlic Cloves",
            "Extra Virgin Olive Oil",
            "Feta Cheese",
        ],
        "instructions": (
            "1. Sauté garlic in olive oil in a saucepan until fragrant.\n"
            "2. Add jasmine rice and toast for 2 minutes.\n"
            "3. Add water/broth and simmer covered for 18 minutes.\n"
            "4. Fold in crumbled feta cheese before serving."
        ),
    },
]


def search_recipes(
    query: str | None = None,
    max_prep_time_minutes: int | None = None,
    dietary_restriction: str | None = None,
    ingredients: str | None = None,
) -> str:
    """Searches for recipes matching available ingredients, maximum prep time, and dietary restrictions.

    Args:
        query: Optional general search keyword (e.g. 'chicken', 'mediterranean', 'salad').
        max_prep_time_minutes: Maximum prep/cook time in minutes (e.g. 30).
        dietary_restriction: Required dietary constraint (e.g. 'Gluten-Free', 'Dairy-Free', 'Nut-Free').
        ingredients: Comma-separated list of ingredients to match (e.g. 'chicken, rice, broccoli').

    Returns:
        A formatted string listing matching recipes with prep time, ingredients, and instructions.
    """
    results = RECIPE_CATALOG

    if query:
        q = query.lower().strip()
        results = [
            r
            for r in results
            if q in r["title"].lower()
            or q in r["id"]
            or any(q in ing.lower() for ing in r["ingredients"])
        ]

    if max_prep_time_minutes is not None:
        results = [r for r in results if r["prep_time_minutes"] <= max_prep_time_minutes]

    if dietary_restriction:
        d = dietary_restriction.lower().strip()
        results = [
            r
            for r in results
            if any(d in tag.lower() for tag in r["dietary_tags"])
        ]

    if ingredients:
        ing_list = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
        if ing_list:
            results = [
                r
                for r in results
                if any(any(user_ing in ing.lower() for ing in r["ingredients"]) for user_ing in ing_list)
            ]

    if not results:
        return "No recipes found matching the specified criteria."

    formatted = []
    for r in results:
        recipe_str = (
            f"📖 **{r['title']}**\n"
            f"- Prep/Cook Time: {r['prep_time_minutes']} minutes\n"
            f"- Servings: {r['servings']}\n"
            f"- Dietary Tags: {', '.join(r['dietary_tags'])}\n"
            f"- Ingredients: {', '.join(r['ingredients'])}\n"
            f"- Instructions:\n{r['instructions']}"
        )
        formatted.append(recipe_str)

    return "\n\n---\n\n".join(formatted)
