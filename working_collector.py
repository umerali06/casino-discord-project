#!/usr/bin/env python3
"""
Working Roulette Results Collector for BetFury
Actually connects to browser and detects results
"""

import time
import logging
import signal
import sys
import json
from datetime import datetime
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import Config
from discord_notifier import DiscordNotifier
from local_html_client import LocalHTMLClient
from roulette_result import RouletteResult, get_color_for_number

class WorkingRouletteCollector:
    """Working collector that actually connects to browser and detects results"""
    
    def __init__(self):
        self.discord = DiscordNotifier()
        self.local_html = LocalHTMLClient()
        self.logger = self._setup_logging()
        self.driver = None
        self.running = False
        self.last_result = None
        self.stats = {
            "results_collected": 0,
            "discord_sent": 0,
            "local_html_sent": 0,
            "errors": 0,
            "start_time": None
        }
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def connect_to_browser(self) -> bool:
        try:
            self.logger.info("Starting Chrome browser...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"--window-size={Config.BROWSER_WIDTH},{Config.BROWSER_HEIGHT}")
            
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return self._navigate_to_betfury()
            
        except Exception as e:
            self.logger.error(f"Failed to start Chrome: {str(e)}")
            return False
    
    def _navigate_to_betfury(self) -> bool:
        try:
            self.logger.info(f"Navigating to BetFury: {Config.CASINO_URL}")
            self.driver.get(Config.CASINO_URL)
            
            # Wait for page to load completely
            self.logger.info("Waiting for page to load...")
            time.sleep(10)  # Initial wait for page load
            
            # Wait for page to be ready
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                self.logger.info("Page loaded completely")
            except TimeoutException:
                self.logger.warning("Page load timeout, but continuing...")
            
            # Additional wait for dynamic content
            self.logger.info("Waiting for dynamic content to load...")
            time.sleep(15)  # Wait for JavaScript to load
            
            # Check if we're on the right page
            current_url = self.driver.current_url
            self.logger.info(f"Current URL: {current_url}")
            
            if "betfury.io" in current_url or "evolution" in current_url.lower():
                self.logger.info("Successfully loaded BetFury page")
                return True
            else:
                self.logger.warning(f"Not on expected page. Current URL: {current_url}")
                return True  # Continue anyway, might be redirected
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to BetFury: {str(e)}")
            return False
    
    def detect_result(self) -> Optional[RouletteResult]:
        try:
            if not self.driver:
                return None
            
            # Check if page is still accessible
            try:
                current_url = self.driver.current_url
                if not current_url:
                    self.logger.warning("Page not accessible, skipping detection")
                    return None
            except WebDriverException:
                self.logger.warning("Browser connection lost, skipping detection")
                return None
            
            # Comprehensive list of selectors for Evolution Gaming roulette on BetFury
            selectors = [
                # BetFury specific selectors
                ".evo-roulette-result", ".evo-result-number", ".evo-winning-number",
                ".evo-game-result", ".evo-roulette-number", ".evo-result-display",
                
                # Evolution Gaming specific selectors
                ".evolution-roulette-result", ".evolution-result-number",
                ".evolution-winning-number", ".evolution-game-result",
                
                # Generic roulette selectors
                ".result-number", ".roulette-result", ".game-result", ".winning-number",
                ".last-result", ".previous-result", ".current-result",
                
                # Data attributes
                "[data-result]", "[data-number]", "[data-winning-number]",
                "[data-roulette-result]", "[data-game-result]",
                
                # Display elements
                ".number-display", ".result-display", ".winning-number-display",
                ".roulette-number", ".game-number", ".result-number-display",
                
                # BetFury specific variations
                ".bf-roulette-result", ".bf-result-number", ".bf-winning-number",
                ".bf-game-result", ".bf-roulette-number",
                
                # Live game selectors
                ".live-game-result", ".live-roulette-result", ".live-result-number",
                ".live-winning-number", ".live-game-number",
                
                # More specific selectors
                ".evo-roulette .result", ".evo-roulette .number", ".evo-roulette .winning",
                ".evo-game .result", ".evo-game .number", ".evo-game .winning",
                ".roulette-game .result", ".roulette-game .number", ".roulette-game .winning",
                
                # Additional variations
                ".number-result", ".winning-result", ".last-winning-number",
                ".displayed-number", ".game-number-display", ".result-number-text"
            ]
            
            for selector in selectors:
                try:
                    # Wait a bit for elements to be present
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        try:
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
                                    self.logger.info(f"Result detected via {selector}: {number} ({color})")
                                    return result
                                    
                        except Exception as e:
                            self.logger.debug(f"Error processing element with selector {selector}: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {str(e)}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting result: {str(e)}")
            return None
    
    def _is_valid_number(self, text: str) -> bool:
        try:
            number = int(text)
            return 0 <= number <= 36
        except ValueError:
            return False
    
    def _is_new_result(self, result: RouletteResult) -> bool:
        if not self.last_result:
            return True
        
        # Check if it's the same number and within a short time window
        if (result.number == self.last_result.number and 
            (result.timestamp - self.last_result.timestamp).seconds < 30):
            return False
        
        return True
    
    def _get_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def start(self) -> bool:
        try:
            self.logger.info("Starting Working Roulette Results Collector...")
            
            Config.create_directories()
            
            if not self.connect_to_browser():
                self.logger.error("Failed to connect to browser")
                return False
            
            # Send startup notification
            try:
                self.discord.send_startup_message()
            except Exception as e:
                self.logger.warning(f"Failed to send Discord startup message: {str(e)}")
            
            # Test local HTML connection
            try:
                self.local_html.test_connection()
            except Exception as e:
                self.logger.warning(f"Local HTML connection test failed: {str(e)}")
            
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            self.logger.info("Working Roulette Collector started successfully!")
            self.logger.info(f"Monitoring: {Config.TABLE_NAME}")
            self.logger.info("Press Ctrl+C to stop")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start collector: {str(e)}")
            return False
    
    def run(self):
        if not self.start():
            return
        
        try:
            while self.running:
                self._process_cycle()
                time.sleep(Config.SCAN_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            self.stop()
    
    def _process_cycle(self):
        try:
            result = self.detect_result()
            if result:
                self._handle_new_result(result)
            
        except Exception as e:
            self.logger.error(f"Error in process cycle: {str(e)}")
            self.stats["errors"] += 1
    
    def _handle_new_result(self, result: RouletteResult):
        try:
            self.logger.info(f"New result detected: {result.number} ({result.color})")
            self.stats["results_collected"] += 1
            self.last_result = result
            
            # Send to Discord
            try:
                if self.discord.send_result(result):
                    self.stats["discord_sent"] += 1
                    self.logger.info("Result sent to Discord successfully")
                else:
                    self.logger.error("Failed to send result to Discord")
                    self.stats["errors"] += 1
            except Exception as e:
                self.logger.error(f"Discord error: {str(e)}")
                self.stats["errors"] += 1
            
            # Send to local HTML
            try:
                if self.local_html.send_result(result):
                    self.stats["local_html_sent"] += 1
                    self.logger.info("Result sent to local HTML successfully")
                else:
                    self.logger.warning("Failed to send result to local HTML")
            except Exception as e:
                self.logger.warning(f"Local HTML error: {str(e)}")
            
            # Save result to file
            self._save_result(result)
            
        except Exception as e:
            self.logger.error(f"Error handling new result: {str(e)}")
            self.stats["errors"] += 1
    
    def _save_result(self, result: RouletteResult):
        try:
            filename = f"{Config.DATA_DIR}/results_{datetime.now().strftime('%Y%m%d')}.json"
            
            try:
                with open(filename, 'r') as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
            
            results.append(result.to_dict())
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving result to file: {str(e)}")
    
    def stop(self):
        if not self.running:
            return
        
        self.logger.info("Stopping Working Roulette Results Collector...")
        self.running = False
        
        try:
            # Send shutdown notification
            try:
                self.discord.send_shutdown_message()
            except Exception as e:
                self.logger.warning(f"Failed to send Discord shutdown message: {str(e)}")
            
            # Close browser
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("Browser closed successfully")
                except Exception as e:
                    self.logger.error(f"Error closing browser: {str(e)}")
            
            # Print final statistics
            self._print_final_stats()
            self.logger.info("Working Roulette Collector stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    def _print_final_stats(self):
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            self.logger.info(f"Runtime: {runtime}")
        
        self.logger.info("Final Statistics:")
        self.logger.info(f"  Results Collected: {self.stats['results_collected']}")
        self.logger.info(f"  Discord Sent: {self.stats['discord_sent']}")
        self.logger.info(f"  Local HTML Sent: {self.stats['local_html_sent']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")

def main():
    print("Working Roulette Results Collector for BetFury")
    print("=" * 60)
    print("This collector will:")
    print("1. Start Chrome browser")
    print("2. Navigate to BetFury roulette")
    print("3. Wait for page to load completely")
    print("4. Detect results automatically")
    print("5. Send to Discord and local HTML")
    print("=" * 60)
    
    collector = WorkingRouletteCollector()
    
    try:
        collector.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
