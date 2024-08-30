from dataclasses import dataclass
from datetime import datetime


@dataclass
class BetUser:
    time: datetime
    user_id: str
    user_name: str
    text: str
