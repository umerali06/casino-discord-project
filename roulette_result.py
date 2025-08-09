from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

@dataclass
class RouletteResult:
    """Data class representing a roulette result"""
    number: int
    color: str  # 'red', 'black', 'green'
    timestamp: datetime
    table_name: str
    session_id: Optional[str] = None
    
    # Additional properties
    @property
    def is_even(self) -> bool:
        """Check if the number is even"""
        return self.number % 2 == 0
    
    @property
    def is_odd(self) -> bool:
        """Check if the number is odd"""
        return self.number % 2 == 1
    
    @property
    def dozen(self) -> int:
        """Get the dozen (1-12, 13-24, 25-36)"""
        if self.number == 0:
            return 0
        return ((self.number - 1) // 12) + 1
    
    @property
    def column(self) -> int:
        """Get the column (1, 2, or 3)"""
        if self.number == 0:
            return 0
        return ((self.number - 1) % 3) + 1
    
    @property
    def high_low(self) -> str:
        """Get high (19-36) or low (1-18)"""
        if self.number == 0:
            return "zero"
        return "high" if self.number >= 19 else "low"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "number": self.number,
            "color": self.color,
            "timestamp": self.timestamp.isoformat(),
            "table_name": self.table_name,
            "session_id": self.session_id,
            "is_even": self.is_even,
            "is_odd": self.is_odd,
            "dozen": self.dozen,
            "column": self.column,
            "high_low": self.high_low
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RouletteResult':
        """Create RouletteResult from dictionary"""
        return cls(
            number=data["number"],
            color=data["color"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            table_name=data["table_name"],
            session_id=data.get("session_id")
        )
    
    def __str__(self) -> str:
        return f"RouletteResult(number={self.number}, color={self.color}, timestamp={self.timestamp})"
    
    def __repr__(self) -> str:
        return self.__str__()

# Roulette number to color mapping
ROULETTE_COLORS = {
    0: "green",
    1: "red", 2: "black", 3: "red", 4: "black", 5: "red", 6: "black", 7: "red", 8: "black", 9: "red", 10: "black",
    11: "black", 12: "red", 13: "black", 14: "red", 15: "black", 16: "red", 17: "black", 18: "red", 19: "red", 20: "black",
    21: "red", 22: "black", 23: "red", 24: "black", 25: "red", 26: "black", 27: "red", 28: "black", 29: "black", 30: "red",
    31: "black", 32: "red", 33: "black", 34: "red", 35: "black", 36: "red"
}

def get_color_for_number(number: int) -> str:
    """Get the color for a given roulette number"""
    return ROULETTE_COLORS.get(number, "unknown")
