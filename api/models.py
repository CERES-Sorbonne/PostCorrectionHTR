from dataclasses import dataclass
from typing import Optional
from PIL import Image

@dataclass
class LineInfo:
    """Structure pour stocker les informations d'une ligne."""
    id: str
    content: str
    hpos: int | float
    vpos: int | float
    width: int | float
    height: int | float


@dataclass
class WordContext:
    """Structure pour le contexte d'un mot."""
    word: str
    current_line: str
    previous_line: Optional[str]
    next_line: Optional[str]
    cropped_image: bytes
    xml_file: str
    line_index: int | float