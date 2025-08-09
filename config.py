import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the roulette collector"""
    
    # Discord Configuration
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1403803810345910313/b6GOWbVb3mLUnPNnWkR9UsfNAjL6SErKl7bKNydHH7R_cM3og9qE6rdTCYdo_o8318D2")
    
    # Casino Configuration
    CASINO_URL = os.getenv("CASINO_URL", "https://betfury.io/casino/games/immersive-roulette-by-evolution")
    TABLE_NAME = os.getenv("TABLE_NAME", "Immersive Roulette (BetFury)")
    
    # Browser Configuration
    BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", "1920"))
    BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", "1080"))
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "120"))  # 2 hours
    AUTO_RECONNECT = os.getenv("AUTO_RECONNECT", "true").lower() == "true"
    RECONNECT_DELAY_SECONDS = int(os.getenv("RECONNECT_DELAY_SECONDS", "30"))
    
    # Scanning Configuration
    SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "1"))
    RESULT_HISTORY_SIZE = int(os.getenv("RESULT_HISTORY_SIZE", "100"))
    
    # Local HTML System
    LOCAL_HTML_ENDPOINT = os.getenv("LOCAL_HTML_ENDPOINT", "http://localhost:3001/result")
    ENABLE_LOCAL_HTML = os.getenv("ENABLE_LOCAL_HTML", "true").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "roulette_collector.log")
    
    # OCR Configuration (optional)
    OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.7"))
    
    # Directory Configuration
    DATA_DIR = os.getenv("DATA_DIR", "data")
    SCREENSHOTS_DIR = os.getenv("SCREENSHOTS_DIR", "screenshots")
    
    # Notification Configuration
    ENABLE_DISCORD_NOTIFICATIONS = os.getenv("ENABLE_DISCORD_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_CONSOLE_NOTIFICATIONS = os.getenv("ENABLE_CONSOLE_NOTIFICATIONS", "true").lower() == "true"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        import os
        directories = [cls.DATA_DIR, cls.SCREENSHOTS_DIR, "logs"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
