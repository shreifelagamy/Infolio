"""Base crew class for all AI crews"""

import yaml
import os
from typing import Dict, Any
from crewai import Crew

class BaseCrew:
    """Base class for all AI crews"""
    
    def __init__(self, crew_name: str):
        """Initialize base crew with specific crew name"""
        self.crew_name = crew_name
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config', 'crews', crew_name)
        
    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = os.path.join(self.config_dir, filename)
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
            
    @property
    def agents_config(self) -> Dict[str, Any]:
        """Load agents configuration"""
        return self.load_config('agents.yaml')
        
    @property
    def tasks_config(self) -> Dict[str, Any]:
        """Load tasks configuration"""
        return self.load_config('tasks.yaml')
