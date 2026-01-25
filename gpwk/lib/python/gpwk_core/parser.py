"""GPWK notation parser with completion detection."""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from .models import ParsedCapture


class GPWKParser:
    """Parser for GPWK capture notation."""

    # Past tense verbs indicating completion
    PAST_TENSE_VERBS = [
        "took", "did", "completed", "finished", "attended", "went",
        "reviewed", "created", "built", "wrote", "read", "sent",
        "called", "met", "fixed", "updated", "added", "removed",
        "bought", "purchased", "ordered", "scheduled", "booked",
        "delivered", "submitted", "published", "deployed", "released",
        "tested", "verified", "confirmed", "approved", "signed",
        "paid", "transferred", "registered", "enrolled", "joined",
        "wrapped", "packed", "prepared", "organized", "planned",
        "researched", "learned", "studied", "watched", "listened",
        "cleaned", "washed", "cooked", "made", "helped", "taught"
    ]

    # Explicit completion markers
    COMPLETION_MARKERS = [
        "this is complete",
        "already done",
        "finished",
        "completed",
        "done"
    ]

    def parse_capture_notation(self, text: str) -> ParsedCapture:
        """
        Parse GPWK capture notation.

        Supports:
        - Type markers: [AI], [P], or no marker (capture)
        - Priority: !high, !medium, !low, !urgent
        - Energy: ~deep, ~shallow, ~quick
        - Completion detection: past tense, time ranges, explicit markers

        Examples:
            "fix login bug [P] !high ~deep"
            "I took the dog for a walk between 9-10 AM. This is complete."
            "research API best practices [AI] ~shallow"

        Args:
            text: Raw capture text

        Returns:
            ParsedCapture with extracted metadata
        """
        original_text = text
        markers = []

        # Detect completion status
        is_completed, time_range = self._detect_completion(text)
        if is_completed:
            markers.append("completed")

        # Extract type marker
        task_type, type_label = self._extract_type(text)
        if type_label:
            text = text.replace(f"[{type_label}]", "").strip()

        # Extract priority
        priority = self._extract_priority(text)
        if priority:
            # Remove priority marker
            text = re.sub(r"!(?:high|medium|low|urgent)", "", text, flags=re.IGNORECASE).strip()

        # Extract energy
        energy = self._extract_energy(text)
        if energy:
            # Remove energy marker
            text = re.sub(r"~(?:deep|shallow|quick)", "", text, flags=re.IGNORECASE).strip()

        # Clean up title
        title = self._clean_title(text, is_completed, time_range)

        # Build labels list
        labels = self._build_labels(task_type, priority, energy)

        # Build body
        body = self._build_body(original_text, is_completed, time_range)

        return ParsedCapture(
            title=title,
            type=task_type,
            labels=labels,
            body=body,
            is_completed=is_completed,
            priority=priority,
            energy=energy,
            time_range=time_range,
            markers=markers
        )

    def _detect_completion(self, text: str) -> Tuple[bool, Optional[Tuple[str, str]]]:
        """
        Detect if this is a completed activity.

        Returns:
            (is_completed, time_range)
        """
        text_lower = text.lower()

        # Check for explicit completion markers
        for marker in self.COMPLETION_MARKERS:
            if marker in text_lower:
                time_range = self._extract_time_range(text)
                return True, time_range

        # Check for past tense verbs at start
        first_word = text_lower.split()[0] if text.split() else ""
        if first_word in self.PAST_TENSE_VERBS:
            # First word is past tense, this is completed
            time_range = self._extract_time_range(text)
            return True, time_range
        elif first_word == "i":
            # Check if second word is past tense (e.g., "I took...")
            words = text_lower.split()
            if len(words) > 1 and words[1] in self.PAST_TENSE_VERBS:
                time_range = self._extract_time_range(text)
                return True, time_range

        # Check for time range (often indicates completed activity)
        time_range = self._extract_time_range(text)
        if time_range:
            return True, time_range

        return False, None

    def _extract_time_range(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Extract time range from text.

        Supports formats:
        - "between 9:00 AM - 10:00 AM"
        - "from 11:30 AM to 12:30 PM"
        - "from 9-10 AM"
        - "9:00-10:00"
        - "at 9:00 AM"
        """
        # Pattern: "between HH:MM [AM/PM] - HH:MM [AM/PM]"
        match = re.search(
            r"between\s+(\d{1,2}):?(\d{2})?\s*([ap]m)?\s*-\s*(\d{1,2}):?(\d{2})?\s*([ap]m)?",
            text,
            re.IGNORECASE
        )
        if match:
            hour1, min1, period1, hour2, min2, period2 = match.groups()
            time1 = self._format_time(hour1, min1 or "00", period1)
            time2 = self._format_time(hour2, min2 or "00", period2 or period1)
            return (time1, time2)

        # Pattern: "from HH:MM AM to HH:MM PM"
        match = re.search(
            r"from\s+(\d{1,2}):(\d{2})\s*([ap]m)?\s+to\s+(\d{1,2}):(\d{2})\s*([ap]m)?",
            text,
            re.IGNORECASE
        )
        if match:
            hour1, min1, period1, hour2, min2, period2 = match.groups()
            time1 = self._format_time(hour1, min1, period1)
            time2 = self._format_time(hour2, min2, period2 or period1)
            return (time1, time2)

        # Pattern: "from H-H [AM/PM]"
        match = re.search(
            r"from\s+(\d{1,2})\s*-\s*(\d{1,2})\s*([ap]m)?",
            text,
            re.IGNORECASE
        )
        if match:
            hour1, hour2, period = match.groups()
            time1 = self._format_time(hour1, "00", period)
            time2 = self._format_time(hour2, "00", period)
            return (time1, time2)

        # Pattern: "HH:MM AM - HH:MM PM" (with AM/PM markers)
        match = re.search(
            r"(\d{1,2}):(\d{2})\s*([ap]m)\s*-\s*(\d{1,2}):(\d{2})\s*([ap]m)",
            text,
            re.IGNORECASE
        )
        if match:
            hour1, min1, period1, hour2, min2, period2 = match.groups()
            time1 = self._format_time(hour1, min1, period1)
            time2 = self._format_time(hour2, min2, period2)
            return (time1, time2)

        # Pattern: "HH:MM-HH:MM" (24-hour format, no AM/PM)
        match = re.search(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", text)
        if match:
            hour1, min1, hour2, min2 = match.groups()
            return (f"{hour1.zfill(2)}:{min1}", f"{hour2.zfill(2)}:{min2}")

        return None

    def _format_time(self, hour: str, minute: str, period: Optional[str]) -> str:
        """Format time as HH:MM."""
        hour_int = int(hour)

        if period:
            # Convert 12-hour to 24-hour
            if period.lower() == "pm" and hour_int != 12:
                hour_int += 12
            elif period.lower() == "am" and hour_int == 12:
                hour_int = 0

        return f"{hour_int:02d}:{minute}"

    def _extract_type(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Extract task type from markers.

        Returns:
            (type_value, marker_text)
        """
        if "[AI]" in text or "[ai]" in text:
            return ("ai-task", "AI")
        elif "[P]" in text or "[p]" in text:
            return ("task", "P")
        else:
            return ("capture", None)

    def _extract_priority(self, text: str) -> Optional[str]:
        """Extract priority from markers."""
        text_lower = text.lower()

        if "!high" in text_lower or "!urgent" in text_lower:
            return "high"
        elif "!medium" in text_lower:
            return "medium"
        elif "!low" in text_lower:
            return "low"

        return None

    def _extract_energy(self, text: str) -> Optional[str]:
        """Extract energy level from markers."""
        text_lower = text.lower()

        if "~deep" in text_lower:
            return "deep"
        elif "~shallow" in text_lower:
            return "shallow"
        elif "~quick" in text_lower:
            return "quick"

        return None

    def _clean_title(
        self,
        text: str,
        is_completed: bool,
        time_range: Optional[Tuple[str, str]]
    ) -> str:
        """Clean up title text."""
        # Remove completion markers
        for marker in self.COMPLETION_MARKERS:
            text = text.replace(marker, "")
            text = text.replace(marker.title(), "")

        # Remove time range text
        if time_range:
            text = re.sub(
                r"between\s+[\d:apm\s-]+",
                "",
                text,
                flags=re.IGNORECASE
            )
            text = re.sub(
                r"from\s+[\d:apm\s-]+",
                "",
                text,
                flags=re.IGNORECASE
            )

        # Clean up
        text = text.strip()
        text = re.sub(r"\s+", " ", text)  # Collapse multiple spaces
        text = text.rstrip(".")

        # If completed and starts with "I", convert to past tense
        if is_completed and text.lower().startswith("i "):
            # Remove "I " and capitalize first letter
            text = text[2:].strip()
            if text:
                text = text[0].upper() + text[1:]

        # Add time range to title if present
        if time_range:
            text = f"{text} ({time_range[0]} - {time_range[1]})"

        return text

    def _build_labels(
        self,
        task_type: str,
        priority: Optional[str],
        energy: Optional[str]
    ) -> List[str]:
        """Build labels list."""
        labels = []

        # Type label
        if task_type == "ai-task":
            labels.append("pwk:ai")
        elif task_type == "task":
            labels.append("pwk:personal")
        else:
            labels.append("pwk:capture")

        # Priority label
        if priority:
            labels.append(f"priority:{priority}")

        # Energy label
        if energy:
            labels.append(f"energy:{energy}")

        return labels

    def _build_body(
        self,
        original_text: str,
        is_completed: bool,
        time_range: Optional[Tuple[str, str]]
    ) -> str:
        """Build issue body."""
        now = datetime.now()
        status = "Completed" if is_completed else "Captured"

        body_parts = [
            f"## {status}",
            f"- **Date**: {now.strftime('%Y-%m-%d %H:%M %p')}",
            f"- **Source**: GPWK Capture",
            ""
        ]

        if is_completed and time_range:
            body_parts.extend([
                "## Time",
                f"- **Duration**: {time_range[0]} - {time_range[1]}",
                ""
            ])

        body_parts.extend([
            "## Context",
            original_text,
            "",
            "## Notes",
            "(Add notes as you work on this)",
        ])

        return "\n".join(body_parts)
