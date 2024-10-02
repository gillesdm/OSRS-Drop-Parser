import os
import json
from datetime import datetime

def ensure_log_directory():
    """Ensure the Logs directory exists."""
    os.makedirs("Logs", exist_ok=True)

def log_data(category, data_type, data):
    """Log data to a file in the Logs directory."""
    ensure_log_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Logs/{category}_{data_type}_{timestamp}.log"
    
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2, ensure_ascii=False)

def log_api_response(category, url, params, response):
    """Log API response data."""
    log_data(category, "api_response", {
        "url": url,
        "params": params,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content": response.text
    })

def log_parsed_data(category, data_type, data):
    """Log parsed data."""
    log_data(category, data_type, data)
