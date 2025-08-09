import requests
import json
import logging
from datetime import datetime
from typing import Optional
from roulette_result import RouletteResult
from config import Config

class DiscordNotifier:
    """Handles Discord webhook notifications for roulette results"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or Config.DISCORD_WEBHOOK_URL
        self.logger = logging.getLogger(__name__)
        
    def send_result(self, result: RouletteResult) -> bool:
        """Send a roulette result to Discord"""
        try:
            embed = self._create_result_embed(result)
            payload = {
                "embeds": [embed],
                "username": "Roulette Results Collector",
                "avatar_url": "https://cdn.discordapp.com/attachments/123456789/roulette_icon.png"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                self.logger.info(f"Result sent to Discord: {result.number} ({result.color})")
                return True
            else:
                self.logger.error(f"Failed to send to Discord: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending to Discord: {str(e)}")
            return False
    
    def send_status_message(self, message: str, color: int = 0x00ff00) -> bool:
        """Send a status message to Discord"""
        try:
            embed = {
                "title": "Roulette Collector Status",
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "embeds": [embed],
                "username": "Roulette Results Collector"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Error sending status to Discord: {str(e)}")
            return False
    
    def _create_result_embed(self, result: RouletteResult) -> dict:
        """Create Discord embed for roulette result"""
        # Color mapping for Discord embeds
        color_map = {
            "red": 0xff0000,
            "black": 0x000000,
            "green": 0x00ff00
        }
        
        embed = {
            "title": f"🎰 Roulette Result: {result.number}",
            "description": self._format_result_description(result),
            "color": color_map.get(result.color, 0x808080),
            "fields": [
                {
                    "name": "Number",
                    "value": str(result.number),
                    "inline": True
                },
                {
                    "name": "Color",
                    "value": result.color.capitalize(),
                    "inline": True
                },
                {
                    "name": "Even/Odd",
                    "value": "Even" if result.is_even else "Odd",
                    "inline": True
                },
                {
                    "name": "Dozen",
                    "value": str(result.dozen) if result.dozen > 0 else "Zero",
                    "inline": True
                },
                {
                    "name": "Column",
                    "value": str(result.column) if result.column > 0 else "Zero",
                    "inline": True
                },
                {
                    "name": "High/Low",
                    "value": result.high_low.capitalize(),
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Table: {result.table_name}"
            },
            "timestamp": result.timestamp.isoformat()
        }
        
        return embed
    
    def _format_result_description(self, result: RouletteResult) -> str:
        """Format the result description for Discord"""
        emoji_map = {
            "red": "🔴",
            "black": "⚫",
            "green": "🟢"
        }
        
        emoji = emoji_map.get(result.color, "⚪")
        return f"{emoji} **{result.number}** ({result.color.capitalize()})"
    
    def send_error_message(self, error: str) -> bool:
        """Send an error message to Discord"""
        return self.send_status_message(f"❌ Error: {error}", color=0xff0000)
    
    def send_startup_message(self) -> bool:
        """Send startup notification to Discord"""
        message = "🚀 Roulette Results Collector started successfully!"
        return self.send_status_message(message, color=0x00ff00)
    
    def send_shutdown_message(self) -> bool:
        """Send shutdown notification to Discord"""
        message = "🛑 Roulette Results Collector stopped."
        return self.send_status_message(message, color=0xffa500)
