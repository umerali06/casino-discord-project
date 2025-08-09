#!/usr/bin/env python3
"""
Test script for Discord webhook functionality
"""

import sys
from datetime import datetime
from discord_notifier import DiscordNotifier
from roulette_result import RouletteResult

def test_discord_webhook():
    """Test Discord webhook functionality"""
    print("Testing Discord webhook...")
    
    # Create test result
    test_result = RouletteResult(
        number=15,
        color="black",
        timestamp=datetime.now(),
        table_name="Immersive Roulette (Test)",
        session_id="test_session"
    )
    
    # Initialize Discord notifier
    discord = DiscordNotifier()
    
    try:
        # Test startup message
        print("Sending startup message...")
        if discord.send_startup_message():
            print("✅ Startup message sent successfully")
        else:
            print("❌ Failed to send startup message")
        
        # Test result message
        print("Sending test result...")
        if discord.send_result(test_result):
            print("✅ Test result sent successfully")
        else:
            print("❌ Failed to send test result")
        
        # Test status message
        print("Sending status message...")
        if discord.send_status_message("Test status message"):
            print("✅ Status message sent successfully")
        else:
            print("❌ Failed to send status message")
        
        print("\nDiscord webhook test completed!")
        
    except Exception as e:
        print(f"❌ Error during Discord test: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_discord_webhook()
    sys.exit(0 if success else 1)
