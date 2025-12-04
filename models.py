from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class ValidationError(Exception):
    pass

@dataclass
class Artwork:
    id: Optional[int]
    title: str
    artist: str
    # year: int
    # style: str
    # price: float
    # created_at: str
    
    def validate(self):
        if not self.title.strip():
            raise ValidationError("Название не может быть пустым")
        if not self.artist.strip():
            raise ValidationError("Имя художника не может быть пустым")
        if self.year < 100 or self.year > datetime.now().year:
            raise ValidationError("Некорректный год создания")
        if self.price < 0:
            raise ValidationError("Цена не может быть отрицательной")