import requests
from urllib.parse import quote
import re

def scrape_duckduckgo_image(keyword: str) -> str:
    """
    Searches DuckDuckGo Images for the given keyword and returns a single image URL.
    """
    encoded_keyword = quote(keyword)
    search_url = f"https://duckduckgo.com/?q={encoded_keyword}&iax=images&ia=images"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error searching DuckDuckGo for '{keyword}': {e}")
        return ""

    # Extract the vqd token required for the API request
    vqd_pattern = re.compile(r'vqd=([\'"]?)(\d+-\d+(?:-\d+)?)\1')
    matches = vqd_pattern.search(response.text)
    if not matches:
        print(f"No vqd token found for '{keyword}'.")
        return ""
    vqd = matches.group(2)

    # Prepare the API request parameters and headers
    api_url = "https://duckduckgo.com/i.js"
    params = {
        "l": "us-en",
        "o": "json",
        "q": keyword,
        "vqd": vqd,
        "f": ",,,",
        "p": "1",
        "v7exp": "a",
    }
    headers_api = {
        "User-Agent": headers["User-Agent"],
        "Referer": search_url,
    }

    try:
        api_response = requests.get(api_url, params=params, headers=headers_api, timeout=10)
        api_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images for '{keyword}': {e}")
        return ""

    try:
        data = api_response.json()
        # Return the first image URL if available.
        if data.get("results"):
            return data["results"][0].get("image", "")
    except (KeyError, ValueError) as e:
        print(f"Error parsing JSON response for '{keyword}': {e}")
        return ""

    return ""

if __name__ == "__main__":
    # Quick test for the scraper
    keywords = ["Eiffel Tower", "Statue of Liberty", "Golden Gate Bridge", "Taj Mahal"]
    for keyword in keywords:
        image_url = scrape_duckduckgo_image(keyword)
        if image_url:
            print(f"Image URL for '{keyword}': {image_url}")
        else:
            print(f"No image URL found for '{keyword}'.")
        print("-" * 20)
