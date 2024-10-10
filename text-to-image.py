import requests, os, io
from PIL import Image

# Ensure the 'images' folder exists
output_dir = "./image"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Gemini AI API Token
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Hugging Face API Token
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
hugging_face_url = (
    "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
)
hugging_face_headers = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}


# Function to query the Hugging Face API for image generation
def query_image_generation(payload):
    response = requests.post(
        hugging_face_url, headers=hugging_face_headers, json=payload
    )
    return response.content


# Function to query Gemini AI API to extract highlights with visual descriptions
def query_gemini_ai(story_text):
    # Enhanced prompt to ask for visual and action-oriented highlights
    summary_prompt = (
        "Please read the following story and extract the main highlights. Focus on key visual descriptions and actions that are critical for understanding the plot:"
        "\n\n" + story_text
    )

    # Prepare the request payload
    payload = {"contents": [{"parts": [{"text": summary_prompt}]}]}

    # Send the POST request to the Gemini AI API
    response = requests.post(
        gemini_url, headers={"Content-Type": "application/json"}, json=payload
    )

    # Return the extracted highlights if the request is successful
    if response.status_code == 200:
        try:
            highlights = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return highlights
        except KeyError:
            print("Error extracting highlights from Gemini AI response.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# Function to augment the highlights with full story context and specify cartoon style for image generation
def augment_highlight_with_context_and_style(story_text, highlight):
    # Provide the full story as context, then focus on the specific highlight, specifying the cartoon style
    return f"Full story context: {story_text}\n\nNow focus on this key moment: {highlight}. Generate an image in a cartoon or animated movie style that captures the essence of this moment."


# Step 1: Read the story from the file
with open("story_result.txt", "r", encoding="utf-8") as file:
    story_text = file.read()

# Step 2: Extract key highlights using Gemini AI
print("Extracting key highlights from the story using Gemini AI...")
highlights = query_gemini_ai(story_text)

if highlights:
    print("Extracted Highlights:\n", highlights)

    # Split the highlights into individual sentences for image generation
    highlight_sentences = highlights.split("\n")

    # Step 3: Generate images for each key highlight using Hugging Face API
    for i, highlight in enumerate(highlight_sentences):
        if highlight.strip():  # Ensure we only process non-empty highlights
            print(f"Generating image for highlight: {highlight}")

            # Augment the highlight with full story context and specify cartoon/animated style
            augmented_prompt = augment_highlight_with_context_and_style(
                story_text, highlight
            )
            print(f"Augmented Prompt for Image Generation: {augmented_prompt}")

            # Query Hugging Face API for image generation
            image_bytes = query_image_generation({"inputs": augmented_prompt})

            # Save the image using PIL
            image = Image.open(io.BytesIO(image_bytes))
            image_path = os.path.join(output_dir, f"highlight_image_{i+1}.png")
            image.save(image_path)
            print(f"Image saved as {image_path}")
else:
    print("No highlights extracted from the story.")
