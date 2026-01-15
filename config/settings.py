import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

PAGE_TITLE = "Turkish Macroeconomic Dashboard"
PAGE_ICON = "🇹🇷"
LAYOUT = "wide"

TCMB_API_KEY = os.getenv("TCMB_API_KEY")

COLORS = {
    "primary": "#E30A17",
    "secondary": "#FFFFFF",
    "accent": "#1E3A5F",
    "positive": "#2ECC71",
    "negative": "#E74C3C",
    "neutral": "#95A5A6",
    "background": "#F8F9FA",
    "card": "#FFFFFF",
}
