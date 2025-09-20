"""
PhantomNet C2 Server Package
"""

__version__ = '1.0.0'
__author__ = 'PhantomNet Team'

from .config import config

def create_app(config_name=None):
    """Application factory pattern"""
    from .app import create_app
    return create_app(config_name)
