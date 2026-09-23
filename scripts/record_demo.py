import os
import time
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = "/config/.gemini/antigravity/brain/e2ff3a8c-2002-4bfe-b0a1-5d6523e32692"
TARGET_URL = "https://smart-culinary-coach-frontend-285881095630.us-east1.run.app"

def record():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=ARTIFACTS_DIR,
            record_video_size={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL)
        page.wait_for_timeout(3000)

        # Prompt 1: Show main app capability - Pantry lookup
        print("Sending Prompt 1: Pantry query...")
        input_box = page.locator("#input")
        input_box.fill("What ingredients do I have in my pantry?")
        page.click("button[type='submit']")

        # Wait for agent response 1 to complete (2nd agent message)
        print("Waiting for response to Prompt 1...")
        page.wait_for_function("document.querySelectorAll('#log .msg.agent').length >= 2", timeout=45000)
        page.wait_for_timeout(6000)

        # Prompt 2: Richer prompt showing tool call + generated image
        print("Sending Prompt 2: Recipe search + Image generation...")
        input_box.fill("Suggest a 15-minute dinner recipe using my pantry items, and generate a gourmet presentation image of the dish.")
        page.click("button[type='submit']")

        # Wait for agent response 2 to complete (3rd agent message with image/recipe)
        print("Waiting for response to Prompt 2...")
        page.wait_for_function("document.querySelectorAll('#log .msg.agent').length >= 3", timeout=60000)
        page.wait_for_timeout(8000)

        video_path = page.video.path()
        context.close()
        browser.close()

        final_video_path = os.path.join(ARTIFACTS_DIR, "demo_video.webm")
        if os.path.exists(video_path):
            if os.path.exists(final_video_path):
                os.remove(final_video_path)
            os.rename(video_path, final_video_path)
            print("Successfully recorded demo video to:", final_video_path)
            return final_video_path

if __name__ == "__main__":
    record()
