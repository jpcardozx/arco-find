"""
Utility functions for ARCO V3 system
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/arco.log")
        ]
    )


def ensure_directories() -> None:
    """Ensure required directories exist"""
    directories = [
        "data/executions",
        "logs",
        "exports", 
        "evidence"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Load JSON file with error handling"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return {}


def save_json_file(filepath: Path, data: Any) -> bool:
    """Save data to JSON file with error handling"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def format_currency(amount: int) -> str:
    """Format amount as currency"""
    return f"${amount:,}"


def calculate_qualification_rate(qualified: int, total: int) -> float:
    """Calculate qualification rate"""
    return qualified / total if total > 0 else 0.0


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.lower()
        return domain.replace('www.', '') if domain else ""
    except:
        return ""


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    return text[:max_length] + "..." if len(text) > max_length else text


def get_timestamp() -> str:
    """Get current timestamp string"""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def parse_phone_number(text: str) -> str:
    """Extract phone number from text"""
    import re
    # Simple phone number extraction
    pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def clean_company_name(name: str) -> str:
    """Clean company name for processing"""
    # Remove common suffixes and clean up
    suffixes = ['inc', 'llc', 'ltd', 'corp', 'company', 'co']
    words = name.lower().split()
    cleaned_words = [w for w in words if w not in suffixes]
    return ' '.join(cleaned_words).title()


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in seconds (average 200 WPM)"""
    word_count = len(text.split())
    return max(int(word_count / 200 * 60), 30)  # Minimum 30 seconds


def batch_process(items: List[Any], batch_size: int = 10):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]