import requests
import json
import logging
from typing import Optional
from roulette_result import RouletteResult
from config import Config

class LocalHTMLClient:
    """Handles communication with local HTML system"""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or Config.LOCAL_HTML_ENDPOINT
        self.logger = logging.getLogger(__name__)
        self.enabled = Config.ENABLE_LOCAL_HTML
        
    def send_result(self, result: RouletteResult) -> bool:
        """Send result to local HTML system"""
        if not self.enabled:
            return True
            
        try:
            payload = result.to_dict()
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code in [200, 201, 204]:
                self.logger.info(f"Result sent to local HTML: {result.number}")
                return True
            else:
                self.logger.warning(f"Local HTML returned {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.warning("Local HTML system not available - continuing without local integration")
            return True
        except Exception as e:
            self.logger.error(f"Error sending to local HTML: {str(e)}")
            return False
    
    def send_batch_results(self, results: list[RouletteResult]) -> bool:
        """Send multiple results to local HTML system"""
        if not self.enabled:
            return True
            
        try:
            payload = {
                "results": [result.to_dict() for result in results],
                "count": len(results)
            }
            
            response = requests.post(
                f"{self.endpoint}/batch",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201, 204]:
                self.logger.info(f"Batch of {len(results)} results sent to local HTML")
                return True
            else:
                self.logger.warning(f"Local HTML batch returned {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.warning("Local HTML system not available for batch send")
            return True
        except Exception as e:
            self.logger.error(f"Error sending batch to local HTML: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to local HTML system"""
        if not self.enabled:
            return True
            
        try:
            response = requests.get(
                f"{self.endpoint}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info("Local HTML system is available")
                return True
            else:
                self.logger.warning(f"Local HTML health check returned {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.warning("Local HTML system not available")
            return False
        except Exception as e:
            self.logger.error(f"Error testing local HTML connection: {str(e)}")
            return False
    
    def get_status(self) -> dict:
        """Get status information about local HTML integration"""
        return {
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "available": self.test_connection() if self.enabled else False
        }
