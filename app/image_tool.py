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

import uuid
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded constants as required
PROJECT_ID = "qwiklabs-gcp-03-7f83d2a066bb"
BUCKET_NAME = "smart-culinary-coach-assets-qwiklabs-gcp-03-7f83d2a066bb"


def generate_dish_image(dish_name: str, tool_context: ToolContext) -> str:
    """Generates a high-resolution food presentation image for a dish, saves it as an artifact,
    and uploads it to Cloud Storage.

    Args:
        dish_name: Name or description of the dish/recipe (e.g., 'Mediterranean Chicken and Rice Bowl').

    Returns:
        The public HTTPS URL of the generated dish image stored in Cloud Storage.
    """
    try:
        # 1. Generate image using gemini-3.1-flash-lite-image in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        prompt = (
            f"A professional food photography shot of {dish_name}. "
            f"Beautifully plated, appetizing, soft warm lighting, gourmet restaurant style."
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        if not response.candidates or not response.candidates[0].content.parts:
            return "Failed to generate image: No image data returned from model."

        part = response.candidates[0].content.parts[0]
        if not hasattr(part, "inline_data") or not part.inline_data or not part.inline_data.data:
            return "Failed to generate image: Inline image bytes missing."

        image_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "image/jpeg"

        # Unique filename
        unique_id = uuid.uuid4().hex[:8]
        filename = f"dish_{unique_id}.jpg"

        # Action 1: Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # Action 2: Upload image bytes directly to GCS bucket without writing local file
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Generated image for '{dish_name}' successfully!\nPublic Image URL: {public_url}"

    except Exception as e:
        return f"Error generating dish image: {e}"
