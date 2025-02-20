from fastapi import FastAPI, HTTPException
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = FastAPI()

@app.get("/extract-body-and-links/")
async def extract_body_and_links(url: str):
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Fetch the webpage content with headers
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the body content
        body = soup.body
        if body is None:
            raise HTTPException(status_code=404, detail="No body tag found in the webpage")

        # Extract all links from the webpage
        links = [a.get('href') for a in soup.find_all('a', href=True)]

        # Return the body content and links as a JSON response
        return {
            "body": body.get_text(strip=True),
            "links": links
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch the webpage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
