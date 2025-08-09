import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from typing import Optional

from roulette_result import RouletteResult, get_color_for_number
from config import Config

class RouletteDetectorStealth:
    """Stealth roulette detector that bypasses anti-bot protections"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.last_result = None
        self.result_history = []
        self.session_start_time = None
    
    def initialize_browser(self) -> bool:
        """Initialize the browser with stealth settings"""
        try:
            chrome_options = Options()
            
            # Stealth settings to avoid detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional stealth arguments
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-field-trial-config")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # Random window size to avoid fingerprinting
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            chrome_options.add_argument(f"--window-size={width},{height}")
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # Additional preferences
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")
            
            # Navigate to the casino with human-like behavior
            self.logger.info("Navigating to casino website...")
            self.driver.get(Config.CASINO_URL)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 7))
            
            # Check if we're blocked
            if self._is_blocked():
                self.logger.warning("Access blocked by Cloudflare. Trying alternative approach...")
                return self._try_alternative_access()
            
            # Simulate human behavior
            self._simulate_human_behavior()
            
            self.session_start_time = datetime.now()
            self.logger.info("Browser initialized successfully with stealth mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            return False
    
    def _is_blocked(self) -> bool:
        """Check if access is blocked by Cloudflare"""
        try:
            page_source = self.driver.page_source.lower()
            blocked_indicators = [
                "sorry, you have been blocked",
                "cloudflare",
                "attention required",
                "checking your browser",
                "please wait while we verify"
            ]
            
            for indicator in blocked_indicators:
                if indicator in page_source:
                    return True
            
            return False
        except:
            return False
    
    def _try_alternative_access(self) -> bool:
        """Try alternative methods to access the site"""
        try:
            # Method 1: Try with different user agent
            self.logger.info("Trying with different user agent...")
            self.driver.quit()
            
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Add random delay
            time.sleep(random.uniform(2, 5))
            self.driver.get(Config.CASINO_URL)
            time.sleep(random.uniform(5, 10))
            
            if not self._is_blocked():
                self.session_start_time = datetime.now()
                self.logger.info("Alternative access successful")
                return True
            
            # Method 2: Try with headless mode
            self.logger.info("Trying headless mode...")
            self.driver.quit()
            
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.get(Config.CASINO_URL)
            time.sleep(random.uniform(3, 7))
            
            if not self._is_blocked():
                self.session_start_time = datetime.now()
                self.logger.info("Headless access successful")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Alternative access failed: {str(e)}")
            return False
    
    def _simulate_human_behavior(self):
        """Simulate human-like behavior to avoid detection"""
        try:
            # Random mouse movements
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                actions.move_by_offset(x, y)
                actions.pause(random.uniform(0.1, 0.5))
                actions.perform()
            
            # Random scrolling
            scroll_amount = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 2))
            
            # Scroll back
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            time.sleep(random.uniform(0.5, 2))
            
        except Exception as e:
            self.logger.debug(f"Human behavior simulation failed: {str(e)}")
    
    def detect_result(self) -> Optional[RouletteResult]:
        """Detect the current roulette result"""
        try:
            # Check if we're still blocked
            if self._is_blocked():
                self.logger.warning("Access blocked, attempting to refresh...")
                if not self.refresh_session():
                    return None
            
            result = self._detect_via_dom()
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting result: {str(e)}")
            return None
    
    def _detect_via_dom(self) -> Optional[RouletteResult]:
        """Detect result via DOM elements"""
        try:
            # Wait for game elements to load
            wait = WebDriverWait(self.driver, 15)
            
            # Expanded list of selectors for better detection
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
                ".displayed-number",
                ".winning-number-display",
                ".roulette-result-number",
                ".game-result-number",
                ".result-display-number",
                ".number-display-result"
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
            time.sleep(random.uniform(3, 7))
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
            "ocr_enabled": False,
            "stealth_mode": True
        }
