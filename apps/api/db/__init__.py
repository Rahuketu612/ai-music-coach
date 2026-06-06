from datetime import datetime, timezone
from typing import Optional, List
from dataclasses import dataclass, field

# In-memory storage for MVP (can be replaced with database later)
_sessions_db: List['PracticeSession'] = []


@dataclass
class PracticeSession:
    """Practice Session model for tracking guitar practice attempts."""
    chord_name: str
    duration_seconds: int
    audio_filename: Optional[str] = None
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audio_score: int = 0
    rhythm_score: int = 0
    feedback_text: str = ""

    @staticmethod
    def get_next_id() -> int:
        """Get the next available session ID."""
        if not _sessions_db:
            return 1
        return max(s.id for s in _sessions_db) + 1

    @staticmethod
    def create(chord_name: str, duration_seconds: int, audio_filename: Optional[str] = None) -> 'PracticeSession':
        """Create a new practice session with placeholder feedback."""
        session = PracticeSession(
            id=PracticeSession.get_next_id(),
            chord_name=chord_name,
            duration_seconds=duration_seconds,
            audio_filename=audio_filename,
        )
        # Generate placeholder feedback
        session.feedback_text = f"You practiced {chord_name}. Keep your rhythm steady and try again slowly."
        session.audio_score = 50  # Placeholder score
        session.rhythm_score = 50  # Placeholder score
        _sessions_db.append(session)
        return session

    @staticmethod
    def get_all() -> List['PracticeSession']:
        """Get all practice sessions, ordered by created_at descending."""
        return sorted(_sessions_db, key=lambda s: s.created_at, reverse=True)

    @staticmethod
    def get_by_id(session_id: int) -> Optional['PracticeSession']:
        """Get a practice session by ID."""
        for session in _sessions_db:
            if session.id == session_id:
                return session
        return None


# Re-export type for use elsewhere
PracticeSessionList = List[PracticeSession]