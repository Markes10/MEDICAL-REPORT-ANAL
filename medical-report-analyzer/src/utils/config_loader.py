import yaml
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yml file
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'config', 
        'config.yml'
    )
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Make configuration available as a singleton
config = load_config()