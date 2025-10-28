from mcp.server.fastmcp import FastMCP
import requests
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("mcp-server")

# ------------------------
# 📝 Tool 1: Add Note
# ------------------------
NOTES_FILE = "notes.txt"

def ensure_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

@mcp.tool()
def add_note(message: str) -> str:
    ensure_file()
    with open(NOTES_FILE, "a") as f:
        f.write(message + "\n")
    return "✅ Note saved!"

# ------------------------
# 🌤 Tool 2: Get Weather
# ------------------------
OPENWEATHER_API_KEY = "8e379f6688b02d17b62c1f8d0e7f4456"

@mcp.tool()
def get_weather(city: str) -> str:
    """
    Returns current weather for a given city using OpenWeatherMap API.
    Example: get_weather("Delhi")
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            return f"❌ Error: {response.get('message', 'City not found')}"

        data = (
            f"🌤 Weather in {response['name']}:\n"
            f"- Condition: {response['weather'][0]['description'].capitalize()}\n"
            f"- Temp: {response['main']['temp']}°C\n"
            f"- Feels like: {response['main']['feels_like']}°C\n"
            f"- Humidity: {response['main']['humidity']}%"
        )
        return data

    except Exception as e:
        return f"❌ Error fetching weather: {e}"
    

# ------------------------
# 📰 Tool 3: Get News
# ------------------------
NEWS_API_KEY = "e1871f4c906f4466afa130559582e890"

@mcp.tool()
def get_news(topic: str = "technology") -> str:
    """
    Fetches top headlines for a given topic using NewsAPI.
    Example: get_news("India") or get_news("sports")
    """
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={NEWS_API_KEY}&language=en&country=in&pageSize=5"
        response = requests.get(url).json()

        if response.get("status") != "ok":
            return f"❌ Error: {response.get('message', 'Failed to fetch news')}"

        articles = response.get("articles", [])
        if not articles:
            return f"📰 No recent news found for '{topic}'."

        headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles[:5])]
        return f"🗞 Top News about {topic}:\n" + "\n".join(headlines)

    except Exception as e:
        return f"❌ Error fetching news: {e}"



# ------------------------
# 🚀 Run Server
# ------------------------
if __name__ == "__main__":
    logging.info("🚀 FastMCP Server is running locally... waiting for Claude")
    try:
        mcp.run()
    except Exception as e:
        logging.error("❌ MCP crashed", exc_info=e)

    while True:
        time.sleep(5)
