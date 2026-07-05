"""
monitor/behavior.py
-------------------
Behavior Analysis Module to detect potentially dangerous activities
(e.g., Ransomware) by calculating file modification rate and entropy.
"""

import math
import time
from collections import Counter, deque
from typing import Any, Dict

class BehaviorAnalyzer:
    """
    Analyzes file events to classify behavior as 'Normal' or 'Suspicious'.
    """

    def __init__(
        self,
        time_window: float = 10.0,
        max_modifications: int = 15,
        entropy_threshold: float = 7.5,
        sample_size: int = 8192
    ) -> None:
        """
        Parameters
        ----------
        time_window       : Time window in seconds to count modifications.
        max_modifications : Max allowed modifications within the time window.
        entropy_threshold : Shannon entropy value above which a file is considered encrypted.
        sample_size       : Number of bytes to read from the start of the file for entropy.
        """
        self.time_window = time_window
        self.max_modifications = max_modifications
        self.entropy_threshold = entropy_threshold
        self.sample_size = sample_size

        # Store timestamps of recent modification/creation events
        self._recent_events: deque[float] = deque()

    def _calculate_entropy(self, file_path: str) -> float:
        """Calculate Shannon entropy of a file's content (reads up to sample_size)."""
        try:
            with open(file_path, "rb") as f:
                data = f.read(self.sample_size)
        except Exception:
            # If we cannot read the file (e.g. locked or deleted), return 0
            return 0.0

        if not data:
            return 0.0

        entropy = 0.0
        length = len(data)
        counts = Counter(data)

        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)

        return entropy

    def _update_and_get_modification_rate(self, current_time: float) -> int:
        """Add current event time and remove events outside the time window."""
        self._recent_events.append(current_time)
        
        # Remove old events
        while self._recent_events and current_time - self._recent_events[0] > self.time_window:
            self._recent_events.popleft()
            
        return len(self._recent_events)

    def process_event(self, record: Dict[str, Any]) -> str:
        """
        Evaluate a single file event.
        
        Returns:
            "Normal" or "Suspicious"
        """
        event_type = record.get("event_type")
        is_directory = record.get("is_directory", False)

        # Only care about file creations or modifications
        if is_directory or event_type not in ("created", "modified"):
            return "Normal"

        current_time = time.time()
        mod_rate = self._update_and_get_modification_rate(current_time)

        # Feature Extraction: We check entropy only if the modification rate is high
        # to save CPU cycles, OR we can check it every time. Let's check it every time
        # the file is modified to be safe, but only flag if both conditions might be met 
        # or if entropy is extremely high.
        
        # For ransomware, we expect high frequency AND high entropy.
        if mod_rate > self.max_modifications:
            file_path = record.get("file_path", "")
            entropy = self._calculate_entropy(file_path)
            
            # Record the features in the event dictionary for logging/debugging
            record["behavior_features"] = {
                "mod_rate": mod_rate,
                "entropy": round(entropy, 3)
            }

            if entropy > self.entropy_threshold:
                record["behavior_classification"] = "Suspicious"
                return "Suspicious"

        # Otherwise
        record["behavior_classification"] = "Normal"
        return "Normal"
