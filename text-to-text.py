import requests, json, os

api_key = os.getenv("GEMINI_API_KEY")

# Define the API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

# Define the prompt
title = "The Little Mermaid"
word_count = 100

prompt = (
    "I will provide you the name of the story, and you have to provide me a narration of the story. "
    "The story should be suitable for children aged 8-12 years and fall under the category of a children's book story. "
    "The story must be strictly of "
    + str(word_count)
    + " words long. Ensure the end of the story ends with a good note. The name of the story is: "
    + title
)

# Prepare the request payload
data = {"contents": [{"parts": [{"text": prompt}]}]}

# Make the POST request to the Gemini API
response = requests.post(
    url, headers={"Content-Type": "application/json"}, data=json.dumps(data)
)

# Parse the response
if response.status_code == 200:
    try:
        result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        # print(response.json()["candidates"][0]["content"]["parts"][0]["text"])

        print(f"Response Body: {result}")

        with open("story_result.txt", "w") as file:
            file.write(result)

        print("Response Body has been written to 'story_result.txt'")

    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
