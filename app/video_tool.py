"""Video generation tool for Smart Culinary Coach using gemini-omni-flash-preview."""

import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-7f83d2a066bb"
BUCKET_NAME = "smart-culinary-coach-assets-qwiklabs-gcp-03-7f83d2a066bb"


def generate_dish_video(prompt: str, tool_context: ToolContext = None) -> str:
    """Generate a short video clip for a dish, food presentation, or cooking technique.

    Args:
        prompt: Detailed prompt describing the food video scene (e.g. 'steam rising off artisan pizza').
        tool_context: ADK ToolContext for saving in-memory artifacts.

    Returns:
        The public HTTPS URL of the uploaded video in Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )
    
    # Generate video using gemini-omni-flash-preview via Interactions API
    response = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=f"Generate a short food video clip: {prompt}",
        generation_config={"response_modalities": ["VIDEO"]},
    )

    video_bytes = None
    mime_type = "video/mp4"

    if hasattr(response, "output_video") and response.output_video:
        video_bytes = getattr(response.output_video, "data", None)
        mime_type = getattr(response.output_video, "mime_type", "video/mp4") or "video/mp4"

    if not video_bytes:
        raise ValueError("Failed to generate video bytes from gemini-omni-flash-preview")

    filename = f"dish_video_{uuid.uuid4().hex[:8]}.mp4"

    # 1. Save artifact to Playground via tool_context in-memory
    if tool_context is not None:
        tool_context.save_artifact(
            filename=filename,
            artifact=types.Part.from_bytes(data=video_bytes, mime_type=mime_type),
        )

    # 2. Upload in-memory bytes directly to public GCS bucket
    gcs_client = storage.Client(project=PROJECT_ID)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
