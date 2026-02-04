
import pymongo
from datetime import datetime, timedelta
import random
import os

# --- API CONFIGURATION PLACEHOLDERS ---
# In a production environment, these should be stored in a .env file
X_API_KEY = os.getenv("X_API_KEY", "YOUR_X_KEY")
NEWSDATA_IO_KEY = os.getenv("NEWSDATA_IO_KEY", "YOUR_NEWSDATA_KEY")
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# --- AOR CONFIGURATION (Single Source of Truth) ---
AOR_CONFIG = {
    "USEUCOM": {
        "lat": 50.0,
        "lon": 15.0,
        "zoom": 3,
        "desc": "Europe, Israel, and Russia focus.",
        "countries": ["Poland", "Ukraine", "Estonia"]
    },
    "USCENTCOM": {
        "lat": 28.0,
        "lon": 53.0,
        "zoom": 4,
        "desc": "Middle East and Central Asia focus.",
        "countries": ["Jordan", "Iraq", "Saudi Arabia"]
    },
    "USINDOPACOM": {
        "lat": 10.0,
        "lon": 160.0,
        "zoom": 1,
        "desc": "The 'Tyranny of Distance': 50% of the Earth's surface.",
        "countries": ["Philippines", "Japan", "Taiwan"]
    }
}

# --- MONGODB SETUP ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.intel_db
collection = db.reports

# generate 100 fake reports for DEMO purposes
def seed_mock_data():
    """Generates synthetic data for UI testing."""
    collection.delete_many({})  # Clear old data for fresh demo

    mock_reports = []
    for _ in range(100):
        aor = random.choice(list(AOR_CONFIG.keys()))
        config = AOR_CONFIG[aor]
        mock_reports.append({
            "ccom": aor,
            "country": random.choice(config["countries"]),
            "lat": config["lat"] + random.uniform(-10, 10),
            "lon": config["lon"] + random.uniform(-10, 10),
            "intensity": random.randint(20, 100),
            "summary": "MOCK INTEL: Detected regional movement pattern.",
            "source": "Synthetic Generator",
            "timestamp": datetime.now() - timedelta(hours=random.randint(1, 48))
        })
    collection.insert_many(mock_reports)
    print("✅ Mock Data Seeded.")


# --- OSINT API CONNECTION HOOKS ---

def fetch_x_intel(query="military movements"):
    """
    HOOK: X (Twitter) API v2
    Use Tweepy library here to stream tweets.
    Useful for: Real-time 'flash' reports and on-the-ground sentiment.
    """
    # auth = tweepy.Client(bearer_token=X_API_KEY)
    # tweets = auth.search_recent_tweets(query=query, ...)
    # parse_and_store(tweets)
    print("🔗 Placeholder: X API Connection Point")
    pass


def fetch_newsdata_intel():
    """
    HOOK: NewsData.io
    Useful for: Aggregating international news by country/category.
    """
    # url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_IO_KEY}&q=military&country=pl,ua"
    # response = requests.get(url).json()
    print("🔗 Placeholder: NewsData.io Connection Point")
    pass


def fetch_gdelt_intel():
    """
    HOOK: GDELT Project (Global Database of Events, Language, and Tone)
    Useful for: High-level geopolitical event mapping (Protest, Conflict, Diplomatic).
    """
    # GDELT provides GeoJSON or CSV feeds of global events.
    # Logic: Fetch GDELT 'EventCode' 190 (Use Conventional Military Force).
    print("🔗 Placeholder: GDELT Project Connection Point")
    pass


if __name__ == "__main__":
    # For the recruiter demo, we run the mock seeder.
    # In production, this script would run as a 'Cron Job' calling the API hooks above.
    seed_mock_data()