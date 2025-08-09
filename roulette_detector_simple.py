import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from typing import Optional

from roulette_result import RouletteResult, get_color_for_number
from config import Config

class RouletteDetectorSimple:
    """Simplified roulette detector that works without OCR dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.last_result = None
        self.result_history = []
        self.session_start_time = None
    
    def initialize_browser(self) -> bool:
        """Initialize the browser for game watching"""
        try:
            chrome_options = Options()
            
            if Config.BROWSER_HEADLESS:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={Config.BROWSER_WIDTH},{Config.BROWSER_HEIGHT}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to the casino
            self.driver.get(Config.CASINO_URL)
            self.session_start_time = datetime.now()
            
            self.logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            return False
    
    def detect_result(self) -> Optional[RouletteResult]:
        """Detect the current roulette result via DOM only"""
        try:
            result = self._detect_via_dom()
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting result: {str(e)}")
            return None
    
    def _detect_via_dom(self) -> Optional[RouletteResult]:
        """Detect result via DOM elements"""
        try:
            # Wait for game elements to load
            wait = WebDriverWait(self.driver, 10)
            
            # Look for result elements in the DOM - expanded list for better detection
            selectors = [
                ".result-number",
                ".roulette-result",
                ".game-result",
                "[data-result]",
                ".number-display",
                ".result-display",
                ".result",
                ".number",
                ".winning-number",
                ".last-result",
                ".previous-result",
                ".winning-number-display",
                ".roulette-number",
                ".game-number",
                ".result-number-display",
                ".number-result",
                ".winning-result",
                ".last-winning-number",
                ".current-result",
                ".displayed-number"
            ]
            
            for selector in selectors:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    text = element.text.strip()
                    
                    if text and self._is_valid_number(text):
                        number = int(text)
                        color = get_color_for_number(number)
                        
                        result = RouletteResult(
                            number=number,
                            color=color,
                            timestamp=datetime.now(),
                            table_name=Config.TABLE_NAME,
                            session_id=self._get_session_id()
                        )
                        
                        if self._is_new_result(result):
                            self.logger.info(f"Result detected via DOM: {number} ({color})")
                            return result
                            
                except (TimeoutException, NoSuchElementException):
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"DOM detection failed: {str(e)}")
            return None
    
    def _is_valid_number(self, text: str) -> bool:
        """Check if text represents a valid roulette number"""
        try:
            number = int(text)
            return 0 <= number <= 36
        except ValueError:
            return False
    
    def _is_new_result(self, result: RouletteResult) -> bool:
        """Check if this is a new result (not duplicate)"""
        if not self.last_result:
            return True
        
        # Check if it's the same number and within a short time window
        if (result.number == self.last_result.number and 
            (result.timestamp - self.last_result.timestamp).seconds < 30):
            return False
        
        return True
    
    def _get_session_id(self) -> str:
        """Generate a session ID for tracking"""
        if self.session_start_time:
            return self.session_start_time.strftime("%Y%m%d_%H%M%S")
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def update_result_history(self, result: RouletteResult):
        """Update the result history"""
        self.last_result = result
        self.result_history.append(result)
        
        # Keep only the last N results
        if len(self.result_history) > Config.RESULT_HISTORY_SIZE:
            self.result_history.pop(0)
    
    def is_session_expired(self) -> bool:
        """Check if the session has expired (2 hours)"""
        if not self.session_start_time:
            return False
        
        elapsed = datetime.now() - self.session_start_time
        return elapsed.total_seconds() > (Config.SESSION_TIMEOUT_MINUTES * 60)
    
    def refresh_session(self) -> bool:
        """Refresh the session by reloading the page"""
        try:
            self.driver.refresh()
            self.session_start_time = datetime.now()
            self.logger.info("Session refreshed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh session: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")
    
    def get_status(self) -> dict:
        """Get detector status"""
        return {
            "browser_active": self.driver is not None,
            "session_start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "session_expired": self.is_session_expired(),
            "last_result": self.last_result.to_dict() if self.last_result else None,
            "result_count": len(self.result_history),
            "ocr_enabled": False
        }
