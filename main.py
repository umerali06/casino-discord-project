#!/usr/bin/env python3
"""
Evolution Gaming Roulette Results Collector
Main application file
"""

import time
import logging
import signal
import sys
import json
from datetime import datetime
from typing import Optional
import keyboard
import schedule

from config import Config
from roulette_detector import RouletteDetector
from discord_notifier import DiscordNotifier
from local_html_client import LocalHTMLClient
from roulette_result import RouletteResult

class RouletteCollector:
    """Main roulette results collector application"""
    
    def __init__(self):
        self.detector = RouletteDetector()
        self.discord = DiscordNotifier()
        self.local_html = LocalHTMLClient()
        self.logger = self._setup_logging()
        self.running = False
        self.stats = {
            "results_collected": 0,
            "discord_sent": 0,
            "local_html_sent": 0,
            "errors": 0,
            "start_time": None
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
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
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self) -> bool:
        """Start the roulette collector"""
        try:
            self.logger.info("Starting Roulette Results Collector...")
            
            # Create necessary directories
            Config.create_directories()
            
            # Initialize browser
            if not self.detector.initialize_browser():
                self.logger.error("Failed to initialize browser")
                return False
            
            # Send startup notification
            self.discord.send_startup_message()
            
            # Test local HTML connection
            self.local_html.test_connection()
            
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            self.logger.info("Roulette Collector started successfully!")
            self.logger.info(f"Monitoring: {Config.TABLE_NAME}")
            self.logger.info(f"Discord Webhook: {Config.DISCORD_WEBHOOK_URL}")
            self.logger.info(f"Local HTML: {Config.LOCAL_HTML_ENDPOINT}")
            self.logger.info("Press Ctrl+C to stop")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start collector: {str(e)}")
            return False
    
    def run(self):
        """Main run loop"""
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
        """Process one cycle of result detection and distribution"""
        try:
            # Check if session needs refresh
            if self.detector.is_session_expired():
                self.logger.info("Session expired, refreshing...")
                if not self.detector.refresh_session():
                    self.logger.error("Failed to refresh session")
                    self.stats["errors"] += 1
                    return
            
            # Detect new result
            result = self.detector.detect_result()
            if result:
                self._handle_new_result(result)
            
        except Exception as e:
            self.logger.error(f"Error in process cycle: {str(e)}")
            self.stats["errors"] += 1
    
    def _handle_new_result(self, result: RouletteResult):
        """Handle a newly detected result"""
        try:
            self.logger.info(f"New result detected: {result.number} ({result.color})")
            self.stats["results_collected"] += 1
            
            # Update detector history
            self.detector.update_result_history(result)
            
            # Send to Discord
            if self.discord.send_result(result):
                self.stats["discord_sent"] += 1
                self.logger.info("Result sent to Discord successfully")
            else:
                self.logger.error("Failed to send result to Discord")
                self.stats["errors"] += 1
            
            # Send to local HTML
            if self.local_html.send_result(result):
                self.stats["local_html_sent"] += 1
                self.logger.info("Result sent to local HTML successfully")
            else:
                self.logger.warning("Failed to send result to local HTML")
            
            # Save result to file
            self._save_result(result)
            
        except Exception as e:
            self.logger.error(f"Error handling new result: {str(e)}")
            self.stats["errors"] += 1
    
    def _save_result(self, result: RouletteResult):
        """Save result to local file"""
        try:
            filename = f"{Config.DATA_DIR}/results_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Load existing results
            try:
                with open(filename, 'r') as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
            
            # Add new result
            results.append(result.to_dict())
            
            # Save back to file
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving result to file: {str(e)}")
    
    def stop(self):
        """Stop the roulette collector"""
        if not self.running:
            return
        
        self.logger.info("Stopping Roulette Results Collector...")
        self.running = False
        
        try:
            # Send shutdown notification
            self.discord.send_shutdown_message()
            
            # Close browser
            self.detector.close()
            
            # Print final statistics
            self._print_final_stats()
            
            self.logger.info("Roulette Collector stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    def _print_final_stats(self):
        """Print final statistics"""
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            self.logger.info(f"Runtime: {runtime}")
        
        self.logger.info("Final Statistics:")
        self.logger.info(f"  Results Collected: {self.stats['results_collected']}")
        self.logger.info(f"  Discord Sent: {self.stats['discord_sent']}")
        self.logger.info(f"  Local HTML Sent: {self.stats['local_html_sent']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
    
    def get_status(self) -> dict:
        """Get current status"""
        return {
            "running": self.running,
            "stats": self.stats,
            "detector": self.detector.get_status(),
            "local_html": self.local_html.get_status()
        }

def main():
    """Main entry point"""
    print("🎰 Evolution Gaming Roulette Results Collector")
    print("=" * 50)
    
    collector = RouletteCollector()
    
    try:
        collector.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
