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

# HARDCODED PROJECT ID as required by prompt (must not use GOOGLE_CLOUD_PROJECT or google.auth.default())
PROJECT_ID = "qwiklabs-gcp-03-7f83d2a066bb"

def seed_pantry():
    db = firestore.Client(project=PROJECT_ID)
    pantry_ref = db.collection("pantry_items")

    initial_items = [
        {
            "item_name": "Chicken Breast",
            "category": "Protein",
            "quantity": 500,
            "unit": "g",
            "notes": "Boneless, skinless in freezer",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Jasmine Rice",
            "category": "Grain",
            "quantity": 2,
            "unit": "kg",
            "notes": "Gluten-free white rice",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Broccoli Florets",
            "category": "Produce",
            "quantity": 300,
            "unit": "g",
            "notes": "Fresh in crisper drawer",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Garlic Cloves",
            "category": "Produce",
            "quantity": 6,
            "unit": "cloves",
            "notes": "Fresh garlic",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Extra Virgin Olive Oil",
            "category": "Pantry",
            "quantity": 750,
            "unit": "ml",
            "notes": "Cold pressed",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Feta Cheese",
            "category": "Dairy",
            "quantity": 200,
            "unit": "g",
            "notes": "Authentic Greek feta, gluten-free",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "item_name": "Vine Tomatoes",
            "category": "Produce",
            "quantity": 4,
            "unit": "items",
            "notes": "Ripe, juicy tomatoes",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    ]

    print(f"Seeding Firestore collection 'pantry_items' in project '{PROJECT_ID}'...")
    for item in initial_items:
        doc_id = item["item_name"].lower().replace(" ", "_")
        pantry_ref.document(doc_id).set(item)
        print(f"  [+] Seeded: {item['item_name']} ({item['quantity']} {item['unit']})")

    print("\n✅ Firestore pantry_items collection seeded successfully!")

if __name__ == "__main__":
    seed_pantry()
