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
from google.cloud import firestore

# HARDCODED PROJECT ID as required (do not use GOOGLE_CLOUD_PROJECT or google.auth.default())
PROJECT_ID = "qwiklabs-gcp-03-7f83d2a066bb"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def get_pantry_items(category: str | None = None) -> str:
    """Reads the active pantry inventory from Firestore database.

    Args:
        category: Optional filter by category (e.g. 'Produce', 'Protein', 'Grain', 'Pantry', 'Dairy').

    Returns:
        A string listing current items in the pantry with quantity, unit, category, and notes.
    """
    try:
        db = _get_firestore_client()
        pantry_ref = db.collection("pantry_items")
        if category:
            query = pantry_ref.where("category", "==", category)
            docs = list(query.stream())
        else:
            docs = list(pantry_ref.stream())

        if not docs:
            return "No pantry items found."

        items = []
        for doc in docs:
            d = doc.to_dict()
            item_str = f"- {d.get('item_name')}: {d.get('quantity')} {d.get('unit')} [{d.get('category')}]"
            if d.get("notes"):
                item_str += f" ({d.get('notes')})"
            items.append(item_str)

        return "Current Pantry Inventory:\n" + "\n".join(items)
    except Exception as e:
        return f"Error retrieving pantry items from Firestore: {e}"


def add_or_update_pantry_item(
    item_name: str,
    quantity: float,
    unit: str,
    category: str = "Pantry",
    notes: str = "",
) -> str:
    """Adds a new item or updates an existing item in the Firestore pantry inventory.

    Args:
        item_name: Name of the ingredient/item (e.g. 'Chicken Breast', 'Garlic Cloves').
        quantity: Amount/quantity available.
        unit: Measurement unit (e.g. 'g', 'kg', 'ml', 'cloves', 'items').
        category: Ingredient category ('Produce', 'Protein', 'Grain', 'Pantry', 'Dairy', 'Spices').
        notes: Optional notes or condition (e.g. 'Fresh', 'Gluten-free').

    Returns:
        Status string confirming update in Firestore.
    """
    try:
        db = _get_firestore_client()
        doc_id = item_name.lower().strip().replace(" ", "_")
        doc_ref = db.collection("pantry_items").document(doc_id)

        data = {
            "item_name": item_name.strip(),
            "quantity": quantity,
            "unit": unit.strip(),
            "category": category.strip(),
            "notes": notes.strip(),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        doc_ref.set(data)
        return f"Successfully updated '{item_name}' in Firestore pantry inventory: {quantity} {unit} [{category}]."
    except Exception as e:
        return f"Error updating pantry item in Firestore: {e}"


def remove_pantry_item(item_name: str) -> str:
    """Removes an ingredient item from the Firestore pantry inventory when used up.

    Args:
        item_name: Name of the item to remove from pantry.

    Returns:
        Status string confirming deletion from Firestore.
    """
    try:
        db = _get_firestore_client()
        doc_id = item_name.lower().strip().replace(" ", "_")
        doc_ref = db.collection("pantry_items").document(doc_id)

        doc = doc_ref.get()
        if not doc.exists:
            return f"Item '{item_name}' not found in Firestore pantry inventory."

        doc_ref.delete()
        return f"Successfully removed '{item_name}' from Firestore pantry inventory."
    except Exception as e:
        return f"Error removing pantry item from Firestore: {e}"
