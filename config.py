import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Discord Webhook Configuration
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403803810345910313/b6GOWbVb3mLUnPNnWkR9UsfNAjL6SErKl7bKNydHH7R_cM3og9qE6rdTCYdo_o8318D2"
    
    # Casino Configuration
    CASINO_URL = "https://www.seguro.bet.br/slots/all/320/evolution/66120-2170889-immersive-roulette?btag=2031177_l315264_nId5159&mode=real"
    TABLE_NAME = "Immersive Roulette"
    
    # Browser Configuration
    BROWSER_HEADLESS = False  # Set to True for headless mode
    BROWSER_WIDTH = 1920
    BROWSER_HEIGHT = 1080
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = 120  # 2 hours
    AUTO_RECONNECT = True
    RECONNECT_DELAY_SECONDS = 30
    
    # Result Collection Settings
    SCAN_INTERVAL_SECONDS = 1  # How often to check for new results
    RESULT_HISTORY_SIZE = 100  # Keep last 100 results in memory
    
    # Local HTML Integration
    LOCAL_HTML_ENDPOINT = "http://localhost:3001/result"  # Default endpoint
    ENABLE_LOCAL_HTML = True
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "roulette_collector.log"
    
    # OCR Configuration (for fallback result detection)
    OCR_ENABLED = True
    OCR_CONFIDENCE_THRESHOLD = 0.7
    
    # File Paths
    DATA_DIR = "data"
    SCREENSHOTS_DIR = "screenshots"
    
    # Notification Settings
    ENABLE_DISCORD_NOTIFICATIONS = True
    ENABLE_CONSOLE_NOTIFICATIONS = True
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
