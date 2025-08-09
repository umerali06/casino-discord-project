# Evolution Gaming Roulette Results Collector

A real-time results collector for Evolution Gaming roulette tables that captures game results directly from the browser and sends them to Discord and local HTML systems.

## Features

- 🎯 **Real-time Detection**: Captures roulette results as they appear on screen
- 🔗 **Discord Integration**: Sends results to Discord via webhook with rich embeds
- 🖥️ **Local HTML Integration**: Forwards results to your local betting simulation system
- 🔄 **Auto-reconnect**: Handles session timeouts and automatically reconnects
- 📊 **Comprehensive Data**: Captures number, color, even/odd, dozen, column, high/low
- 💾 **Local Storage**: Saves all results to JSON files for backup
- 🛡️ **Error Handling**: Robust error handling and logging
- 🎨 **OCR Fallback**: Optical character recognition for reliable result detection

## Requirements

- Windows 11
- Python 3.8+
- Chrome browser
- Internet connection

## Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd roulette-collector
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver** (if not already installed)
   ```bash
   pip install webdriver-manager
   ```

4. **Install Tesseract OCR** (optional, for enhanced detection)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to: `C:\Program Files\Tesseract-OCR\`
   - Add to PATH environment variable

## Configuration

The system is pre-configured with your specific settings:

- **Casino URL**: https://www.seguro.bet.br/slots/all/320/evolution/66120-2170889-immersive-roulette
- **Table**: Immersive Roulette (Evolution Gaming)
- **Discord Webhook**: Already configured
- **Local HTML Endpoint**: http://localhost:3001/result

### Customizing Configuration

Edit `config.py` to modify settings:

```python
# Browser settings
BROWSER_HEADLESS = False  # Set to True for background operation
BROWSER_WIDTH = 1920
BROWSER_HEIGHT = 1080

# Session management
SESSION_TIMEOUT_MINUTES = 120  # 2 hours
AUTO_RECONNECT = True

# Result collection
SCAN_INTERVAL_SECONDS = 1  # How often to check for results

# Local HTML integration
LOCAL_HTML_ENDPOINT = "http://localhost:3001/result"
```

## Usage

### Basic Usage

1. **Start the collector**
   ```bash
   python main.py
   ```

2. **The system will:**
   - Open Chrome browser to the casino
   - Start monitoring for roulette results
   - Send results to Discord
   - Forward results to your local HTML system
   - Save results to local files

3. **Stop the collector**
   - Press `Ctrl+C` in the terminal

### Advanced Usage

#### Headless Mode
Set `BROWSER_HEADLESS = True` in `config.py` to run without visible browser window.

#### Custom Discord Webhook
Update the webhook URL in `config.py`:
```python
DISCORD_WEBHOOK_URL = "your-discord-webhook-url"
```

#### Local HTML Integration
The system sends results to your local HTML system in this format:
```json
{
  "number": 15,
  "color": "black",
  "timestamp": "2024-01-15T14:30:25.123456",
  "table_name": "Immersive Roulette",
  "session_id": "20240115_143025",
  "is_even": false,
  "is_odd": true,
  "dozen": 2,
  "column": 3,
  "high_low": "low"
}
```

## Data Format

Each roulette result includes:

- **Number**: 0-36
- **Color**: red, black, or green
- **Timestamp**: ISO format
- **Table Name**: Game table identifier
- **Session ID**: Unique session identifier
- **Even/Odd**: Boolean
- **Dozen**: 1-3 (0 for zero)
- **Column**: 1-3 (0 for zero)
- **High/Low**: high (19-36), low (1-18), zero (0)

## File Structure

```
roulette-collector/
├── main.py                 # Main application
├── config.py              # Configuration settings
├── roulette_detector.py   # Result detection logic
├── discord_notifier.py    # Discord integration
├── local_html_client.py   # Local HTML integration
├── roulette_result.py     # Data models
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Result storage
│   └── results_YYYYMMDD.json
├── screenshots/          # Debug screenshots
└── logs/                 # Application logs
```

## Troubleshooting

### Common Issues

1. **Browser won't start**
   - Ensure Chrome is installed
   - Check internet connection
   - Try updating Chrome

2. **No results detected**
   - Verify the casino URL is accessible
   - Check if the game is running
   - Enable OCR in config if DOM detection fails

3. **Discord notifications not working**
   - Verify webhook URL is correct
   - Check internet connection
   - Ensure Discord server allows webhooks

4. **Session timeouts**
   - The system automatically handles 2-hour timeouts
   - Manual refresh available via browser

### Logs

Check the log file `roulette_collector.log` for detailed information about:
- Result detection
- Discord notifications
- Local HTML integration
- Errors and warnings

### Debug Mode

Enable debug logging by changing `LOG_LEVEL = "DEBUG"` in `config.py`.

## Security Notes

- The system runs locally on your machine
- No data is sent to external servers except Discord
- Webhook URLs should be kept private
- Consider using environment variables for sensitive data

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure Chrome and Tesseract are properly installed
4. Test internet connectivity

## License

This project is for personal use only. Please respect the terms of service of the casino and Evolution Gaming.
