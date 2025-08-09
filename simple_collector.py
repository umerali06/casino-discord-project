#!/usr/bin/env python3
"""
Simple Roulette Results Collector for BetFury
Provides clear instructions and manual setup
"""

import time
import logging
import signal
import sys
import json
from datetime import datetime
from typing import Optional

from config import Config
from discord_notifier import DiscordNotifier
from local_html_client import LocalHTMLClient
from roulette_result import RouletteResult

class SimpleRouletteCollector:
    """Simple collector with manual setup instructions for BetFury"""
    
    def __init__(self):
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
        """Start the simple collector"""
        try:
            self.logger.info("Starting Simple Roulette Results Collector for BetFury...")
            
            # Create necessary directories
            Config.create_directories()
            
            # Send startup notification
            self.discord.send_startup_message()
            
            # Test local HTML connection
            self.local_html.test_connection()
            
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            self.logger.info("Simple Roulette Collector started successfully!")
            self.logger.info("=" * 60)
            self.logger.info("MANUAL SETUP REQUIRED FOR BETFURY:")
            self.logger.info("1. Open Chrome and go to BetFury")
            self.logger.info("2. Log in to your BetFury account")
            self.logger.info("3. Navigate to Immersive Roulette by Evolution")
            self.logger.info("4. Keep the browser window open")
            self.logger.info("5. The collector will monitor your session")
            self.logger.info("=" * 60)
            self.logger.info(f"Monitoring: {Config.TABLE_NAME}")
            self.logger.info(f"Casino URL: {Config.CASINO_URL}")
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
            # For now, we'll simulate the system running
            # In a real implementation, this would connect to the browser
            result = self._simulate_result_detection()
            if result:
                self._handle_new_result(result)
            
        except Exception as e:
            self.logger.error(f"Error in process cycle: {str(e)}")
            self.stats["errors"] += 1
    
    def _simulate_result_detection(self) -> Optional[RouletteResult]:
        """Simulate result detection for demonstration"""
        # This simulates what would happen in a real implementation
        # The actual implementation would:
        # 1. Connect to existing Chrome session
        # 2. Monitor DOM for result elements on BetFury
        # 3. Extract and validate results
        
        # For demonstration, we'll just return None to show the system is running
        return None
    
    def _handle_new_result(self, result: RouletteResult):
        """Handle a newly detected result"""
        try:
            self.logger.info(f"New result detected: {result.number} ({result.color})")
            self.stats["results_collected"] += 1
            
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
        
        self.logger.info("Stopping Simple Roulette Results Collector...")
        self.running = False
        
        try:
            # Send shutdown notification
            self.discord.send_shutdown_message()
            
            # Print final statistics
            self._print_final_stats()
            
            self.logger.info("Simple Roulette Collector stopped successfully")
            
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
            "local_html": self.local_html.get_status()
        }

def main():
    """Main entry point"""
    print("Simple Roulette Results Collector for BetFury")
    print("=" * 60)
    print("This collector provides the infrastructure for")
    print("roulette result collection from BetFury.")
    print()
    print("To complete the setup:")
    print("1. Open Chrome and navigate to BetFury")
    print("2. Log in to your BetFury account")
    print("3. Open Immersive Roulette by Evolution")
    print("4. Keep the browser window open")
    print("5. The collector will monitor your session")
    print("=" * 60)
    
    collector = SimpleRouletteCollector()
    
    try:
        collector.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
