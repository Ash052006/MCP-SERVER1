from mcp.server.fastmcp import FastMCP
import requests
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("mcp-server")


# ------------------------
# 🌟 Gemini Setup (Common for all Gemini Tools)
# ------------------------
import google.generativeai as genai
import logging

# ✅ Set your Gemini API key directly here
GEMINI_API_KEY = "AIzaSyCEYMipnMvazKf7zdjK8waIXxOdWZXDb6A"  # ← replace with your key
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Free-tier and common Gemini models list
CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.0-pro",
    "gemini-pro",
    "gemini-flash",
]

_WORKING_MODEL = None  # cache working model name


def _find_working_model():
    """Finds and caches the first working Gemini model."""
    global _WORKING_MODEL
    if _WORKING_MODEL:
        return _WORKING_MODEL

    for name in CANDIDATE_MODELS:
        try:
            logging.info(f"🔍 Trying Gemini model: {name}")
            model = genai.GenerativeModel(name)
            test = model.generate_content("Hello")
            if test and test.text:
                _WORKING_MODEL = name
                logging.info(f"✅ Using Gemini model: {name}")
                return _WORKING_MODEL
        except Exception as e:
            logging.warning(f"⚠️ Model {name} failed: {e}")
            continue

    return None




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
# 😄 Tool 4: Chat Mood Analyzer
# ------------------------
@mcp.tool()
def analyze_chat_mood(message: str) -> str:
    """
    Analyze the emotional tone of a message using Gemini API.
    Example:
      analyze_chat_mood("I'm feeling so tired of exams lately")
    """
    try:
        if not message or not message.strip():
            return "⚠️ Please provide a non-empty message."

        model_name = _find_working_model()
        if not model_name:
            return (
                "❌ No working Gemini model found. "
                "Please check your API key or try again later."
            )

        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are an emotion analysis assistant.
        Analyze the tone of this chat message and respond with one short phrase describing the mood.
        Examples:
        - Happy and friendly 😊
        - Angry or irritated 😠
        - Sad or disappointed 😞
        - Neutral and calm 😐

        Message: "{message}"
        """
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "⚠️ No response from Gemini."

    except Exception as e:
        logging.exception("Error in analyze_chat_mood")
        return f"❌ Error analyzing mood: {e}"


# ------------------------
# 🤖 Tool 5: AI Task Prioritizer (uses shared working model finder)
# ------------------------
import google.generativeai as genai
import logging

# Assume the same GEMINI_API_KEY and _find_working_model() from your other file
# are already defined and imported.

@mcp.tool()
def ai_prioritize_tasks(task_list: str) -> str:
    """
    Prioritizes a list of tasks based on importance and urgency using Gemini API.
    Example:
      ai_prioritize_tasks("Finish report, reply to emails, clean desk, buy groceries")
    """
    try:
        if not task_list or not task_list.strip():
            return "⚠️ Please provide a non-empty list of tasks."

        model_name = _find_working_model()
        if not model_name:
            return (
                "❌ No available Gemini model found for your API key. "
                "Please check your key or upgrade your access."
            )

        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are an intelligent assistant. Analyze the following list of tasks
        and rank them by importance and urgency.

        Tasks:
        {task_list}

        Respond concisely with a numbered list in this format:
        1. [Most important/urgent task]
        2. [Next important]
        3. [Less urgent/important task]
        """

        response = model.generate_content(prompt)
        return (
            f"✅ Using Gemini model: {model_name}\n\n" + response.text.strip()
            if response and response.text
            else "⚠️ No response from Gemini."
        )

    except Exception as e:
        logging.exception("Error in ai_prioritize_tasks")
        return f"❌ Error prioritizing tasks: {e}"


# ------------------------
# 💱 Tool 6: Currency Converter with AI Context
# ------------------------
EXCHANGE_API = "https://api.exchangerate.host/convert"

@mcp.tool()
def ai_currency_converter(amount: float, from_currency: str, to_currency: str, context: str = "") -> str:
    """
    Converts currency using real-time rates and adds Gemini's contextual insights.
    Example:
    ai_currency_converter(50000, "INR", "USD", "I'm travelling to the US next month")
    """
    try:
        # --- Step 1: Fetch real-time exchange rate ---
        params = {"from": from_currency.upper(), "to": to_currency.upper(), "amount": amount}
        data = requests.get(EXCHANGE_API, params=params, timeout=10).json()

        if not data.get("result"):
            return f"❌ Conversion failed: {data.get('error', 'No result returned.')}"

        converted = round(data["result"], 2)
        rate = round(data["info"]["rate"], 4)

        # --- Step 2: Find working Gemini model ---
        model_name = _find_working_model()
        if not model_name:
            return (
                "❌ No available Gemini model found for your API key. "
                "Please check your key or upgrade your access."
            )

        # --- Step 3: Generate AI explanation ---
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a helpful financial assistant.
        A user converted {amount} {from_currency} to {to_currency}, resulting in {converted} {to_currency}.
        Context: {context or 'No extra context provided.'}

        Write a short (2–3 lines) natural explanation of this conversion
        and give one practical tip related to this context.
        """

        response = model.generate_content(prompt)
        ai_comment = response.text.strip() if response and response.text else "No AI insight available."

        # --- Step 4: Return formatted response ---
        return (
            f"💱 Currency Conversion Result\n"
            f"---------------------------\n"
            f"Amount: {amount} {from_currency}\n"
            f"Converted: {converted} {to_currency}\n"
            f"Rate: 1 {from_currency} = {rate} {to_currency}\n"
            f"Model Used: {model_name}\n\n"
            f"🤖 AI Insight:\n{ai_comment}"
        )

    except Exception as e:
        logging.exception("Error in ai_currency_converter")
        return f"❌ Error converting currency: {e}"

# ------------------------
# 📄 Tool 7: AI-based Resume Formatter
# ------------------------
import google.generativeai as genai
import logging

@mcp.tool()
def ai_resume_formatter(resume_text: str) -> str:
    """
    Formats and improves a resume using Gemini AI.
    Example:
    ai_resume_formatter("I am a software engineer skilled in python and web dev...")
    """
    try:
        if not resume_text or len(resume_text.split()) < 50:
            return "⚠️ Please provide a detailed resume text (at least 50 words)."

        # 🔍 Find a working Gemini model
        model_name = _find_working_model()
        if not model_name:
            return (
                "❌ No available Gemini model found for your API key. "
                "Please check your key or upgrade your access."
            )

        # 🧠 Generate formatted and improved resume
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a professional HR resume reviewer and formatting expert.
        Reformat and improve the following resume content.
        Keep it ATS-friendly, concise, and neatly structured.
        Focus on:
        - Consistent section titles (e.g., Objective, Skills, Experience, Education)
        - Bullet points where applicable
        - Professional tone and formatting
        - Remove redundancy or grammatical errors

        Resume Content:
        {resume_text}

        Return the formatted resume below:
        """

        response = model.generate_content(prompt)
        return (
            f"🧾 **AI-Formatted Resume (Model: {model_name})**\n\n"
            f"{response.text.strip() if response and response.text else '⚠️ No response from Gemini.'}"
        )

    except Exception as e:
        logging.exception("Error in ai_resume_formatter")
        return f"❌ Error formatting resume: {e}"

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
