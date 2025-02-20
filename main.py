from fastapi import FastAPI, HTTPException
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = FastAPI()

@app.get("/extract-data/")
async def extract_data(url: str):
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Fetch webpage content with appropriate headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Handle HTTP errors

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract body text
        body_tag = soup.body
        if body_tag is None:
            raise HTTPException(status_code=404, detail="No body tag found in the webpage")
        body_text = body_tag.get_text(strip=True)

        # Extract all links
        links = [a.get('href') for a in soup.find_all('a', href=True)]

        # Extract image URLs from <img> tags
        images = [img.get('src') for img in soup.find_all('img', src=True)]

        # Extract headings (h1 to h6) and group by tag
        headings = {}
        for level in range(1, 7):
            tag = f"h{level}"
            headings[tag] = [heading.get_text(strip=True) for heading in soup.find_all(tag)]

        # Extract card contents (assuming elements with class "card")
        cards = [card.get_text(strip=True) for card in soup.find_all(class_="card")]

        # Extract page title
        title = soup.title.get_text(strip=True) if soup.title else None

        # Extract meta description if available
        meta_description = None
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_description = meta_tag.get("content", None)

        # Return all extracted data as JSON
        return {
            "title": title,
            "meta_description": meta_description,
            "body": body_text,
            "links": links,
            "images": images,
            "headings": headings,
            "cards": cards
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch the webpage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
