#!/usr/bin/env python3
"""
Browser Connector for Existing Chrome Session
Connects to running Chrome browser using DevTools Protocol
"""

import time
import logging
import json
import requests
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

class BrowserConnector:
    """Connects to existing Chrome browser session"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.last_result = None
        self.result_history = []
        self.session_start_time = None
    
    def connect_to_existing_browser(self) -> bool:
        """Connect to existing Chrome browser session"""
        try:
            # Method 1: Try to connect to existing Chrome session
            self.logger.info("Attempting to connect to existing Chrome session...")
            
            # Get list of Chrome debug ports
            debug_ports = self._find_chrome_debug_ports()
            
            if not debug_ports:
                self.logger.warning("No Chrome debug ports found. Please start Chrome with --remote-debugging-port=9222")
                return self._start_chrome_with_debug()
            
            # Try to connect to the first available port
            for port in debug_ports:
                if self._connect_to_port(port):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to existing browser: {str(e)}")
            return False
    
    def _find_chrome_debug_ports(self) -> list:
        """Find Chrome debug ports"""
        ports = []
        
        # Common debug ports
        common_ports = [9222, 9223, 9224, 9225, 9226]
        
        for port in common_ports:
            try:
                response = requests.get(f"http://localhost:{port}/json/version", timeout=2)
                if response.status_code == 200:
                    ports.append(port)
                    self.logger.info(f"Found Chrome debug port: {port}")
            except:
                continue
        
        return ports
    
    def _connect_to_port(self, port: int) -> bool:
        """Connect to specific debug port"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{port}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Test if we can access the page
            current_url = self.driver.current_url
            self.logger.info(f"Connected to Chrome session. Current URL: {current_url}")
            
            # Check if we're on the casino page
            if "seguro.bet.br" in current_url or "evolution" in current_url.lower():
                self.logger.info("Already on casino page!")
                self.session_start_time = datetime.now()
                return True
            else:
                self.logger.info("Not on casino page. Navigating...")
                return self._navigate_to_casino()
                
        except Exception as e:
            self.logger.error(f"Failed to connect to port {port}: {str(e)}")
            return False
    
    def _start_chrome_with_debug(self) -> bool:
        """Start Chrome with debugging enabled"""
        try:
            self.logger.info("Starting Chrome with debugging enabled...")
            
            chrome_options = Options()
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--user-data-dir=./chrome_debug_profile")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to casino
            return self._navigate_to_casino()
            
        except Exception as e:
            self.logger.error(f"Failed to start Chrome with debug: {str(e)}")
            return False
    
    def _navigate_to_casino(self) -> bool:
        """Navigate to casino page"""
        try:
            self.logger.info(f"Navigating to casino: {Config.CASINO_URL}")
            self.driver.get(Config.CASINO_URL)
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if we're blocked
            if self._is_blocked():
                self.logger.warning("Access blocked. Please log in manually and refresh the page.")
                return False
            
            self.session_start_time = datetime.now()
            self.logger.info("Successfully connected to casino page")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to casino: {str(e)}")
            return False
    
    def _is_blocked(self) -> bool:
        """Check if access is blocked"""
        try:
            page_source = self.driver.page_source.lower()
            blocked_indicators = [
                "sorry, you have been blocked",
                "cloudflare",
                "attention required",
                "checking your browser"
            ]
            
            for indicator in blocked_indicators:
                if indicator in page_source:
                    return True
            
            return False
        except:
            return False
    
    def detect_result(self) -> Optional[RouletteResult]:
        """Detect roulette result from current page"""
        try:
            # Check if we're still on the right page
            current_url = self.driver.current_url
            if "seguro.bet.br" not in current_url and "evolution" not in current_url.lower():
                self.logger.warning("Not on casino page anymore")
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
            wait = WebDriverWait(self.driver, 10)
            
            # Comprehensive list of selectors for Evolution Gaming roulette
            selectors = [
                # Evolution Gaming specific selectors
                ".evo-roulette-result",
                ".evo-result-number",
                ".evo-winning-number",
                ".evo-game-result",
                
                # Generic roulette selectors
                ".result-number",
                ".roulette-result",
                ".game-result",
                ".winning-number",
                ".last-result",
                ".previous-result",
                
                # Data attributes
                "[data-result]",
                "[data-number]",
                "[data-winning-number]",
                
                # Display elements
                ".number-display",
                ".result-display",
                ".winning-number-display",
                ".roulette-number",
                ".game-number",
                
                # Additional variations
                ".result-number-display",
                ".number-result",
                ".winning-result",
                ".last-winning-number",
                ".current-result",
                ".displayed-number"
            ]
            
            for selector in selectors:
                try:
                    # Try to find element
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
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
                                self.logger.info(f"Result detected via DOM ({selector}): {number} ({color})")
                                return result
                                
                except (TimeoutException, NoSuchElementException):
                    continue
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {str(e)}")
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
            time.sleep(5)
            self.session_start_time = datetime.now()
            self.logger.info("Session refreshed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh session: {str(e)}")
            return False
    
    def close(self):
        """Close the browser connection"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser connection closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser connection: {str(e)}")
    
    def get_status(self) -> dict:
        """Get connector status"""
        return {
            "connected": self.driver is not None,
            "session_start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "session_expired": self.is_session_expired(),
            "last_result": self.last_result.to_dict() if self.last_result else None,
            "result_count": len(self.result_history),
            "current_url": self.driver.current_url if self.driver else None
        }
