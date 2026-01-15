import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Page config
PAGE_TITLE = "Turkish Macroeconomic Dashboard"
PAGE_ICON = "🇹🇷"
LAYOUT = "wide"

# API Keys
TCMB_API_KEY = os.getenv("TCMB_API_KEY")

# Colors
COLORS = {
    "primary": "#E30A17",      # Turkish red
    "secondary": "#FFFFFF",    # White
    "accent": "#1E3A5F",       # Dark blue
    "positive": "#2ECC71",     # Green (good indicators)
    "negative": "#E74C3C",     # Red (bad indicators)
    "neutral": "#95A5A6",      # Gray
    "background": "#F8F9FA",   # Light gray
    "card": "#FFFFFF",         # White cards
}
