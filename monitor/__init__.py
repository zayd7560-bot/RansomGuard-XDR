"""
monitor package
~~~~~~~~~~~~~~~
Exposes the three core components of the File System Monitoring System:
  - FileEventLogger  : JSON-structured rotating-file logger
  - AlertSystem      : Console (and optional e-mail) alert dispatcher
  - FileEventHandler : Watchdog event handler that ties everything together
"""

from .logger  import FileEventLogger
from .alerts  import AlertSystem
from .handler import FileEventHandler

__all__ = ["FileEventLogger", "AlertSystem", "FileEventHandler"]
