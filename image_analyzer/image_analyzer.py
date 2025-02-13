import os
import requests
import base64

def analyze_image(image_url: str) -> dict:
    """
    Downloads the image from the given URL, encodes it in base64,
    and sends it to the GPT-4o API for analysis.

    Args:
        image_url (str): The URL of the image to analyze.

    Returns:
        dict: The JSON response from the API containing the analysis.
    """
    # Retrieve the API key from an environment variable.
    api_key = os.getenv("CHATGPT_4O_KEY")
    if not api_key:
        raise ValueError("Environment variable CHATGPT_4O_KEY is not set. Please set your API key.")

    # Download the image from the provided URL.
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        raise Exception(f"Failed to download image. Status code: {image_response.status_code}")
    
    # Encode the image in base64.
    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
    # Create a data URI (adjust the MIME type if needed).
    data_uri = f"data:image/jpeg;base64,{image_base64}"
    
    # Build the prompt that includes the image data.
    # (Note: Depending on the API's capabilities, you might need to adjust this.)
    prompt = (
        "Please provide a detailed analysis of the content of the image provided below. "
        "Describe the objects present, the context, and any interesting details you can deduce.\n\n"
        "Image Data:\n" + data_uri
    )
    
    # Define the payload for the GPT-4o API.
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "web_access": False
    }
    
    # API endpoint from RapidAPI.
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    
    # Set the headers with your API key.
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    # Send the POST request to the API.
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    # Example usage: Pass the image URL as a command-line argument.
    import sys
    if len(sys.argv) != 2:
        print("Usage: python image_analyzer.py <image_url>")
        sys.exit(1)
    
    test_image_url = sys.argv[1]
    
    try:
        analysis_result = analyze_image(test_image_url)
        print("Analysis Result:")
        print(analysis_result)
    except Exception as e:
        print(f"An error occurred: {e}")




