import base64
import os
from io import BytesIO

from models import LineInfo
import xml.etree.ElementTree as ET
from PIL import Image

def _get_xml_files(xml_directory) -> list[str]:
    """Récupère tous les fichiers XML du répertoire."""
    xml_files = []
    for file in os.listdir(xml_directory):
        if file.endswith('.xml'):
            xml_files.append(os.path.join(xml_directory, file))
    return sorted(xml_files)

def parse_xml_lines(xml_file: str) -> list[LineInfo]:
    """Parse un fichier XML et extrait les informations des lignes."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}

    lines = []

    # Chercher tous les TextLine elements
    for textline in root.findall('.//alto:TextLine', namespace):
        line_id = textline.get('ID', '')
        hpos = int(textline.get('HPOS', 0))
        vpos = int(textline.get('VPOS', 0))
        width = int(textline.get('WIDTH', 0))
        height = int(textline.get('HEIGHT', 0))

        # Récupérer le contenu de la ligne
        string_elem = textline.find('.//alto:String', namespace)
        content = string_elem.get('CONTENT', '') if string_elem is not None else ''

        lines.append(LineInfo(
            id=line_id,
            content=content,
            hpos=hpos,
            vpos=vpos,
            width=width,
            height=height,
        ))

    return lines

def get_bounding_box_for_lines(lines: list[LineInfo]) -> tuple[int, int, int, int]:
    """Calcule la bounding box englobant plusieurs lignes."""
    if not lines:
        return (0, 0, 0, 0)

    min_x = min(line.hpos for line in lines if line is not None)
    min_y = min(line.vpos for line in lines if line is not None)
    max_x = max(line.hpos + line.width for line in lines if line is not None)
    max_y = max(line.vpos + line.height for line in lines if line is not None)

    # Ajouter une marge
    margin = 10
    return (
        max(0, min_x - margin),
        max(0, min_y - margin),
        max_x + margin,
        max_y + margin
    )

def crop_image_for_context(image: Image.Image,
                           current_line: LineInfo,
                           previous_line: [LineInfo],
                           next_line: [LineInfo]) -> bytes:
    """Crée une image croppée contenant le contexte des 3 lignes."""
    lines_to_include = [line for line in [previous_line, current_line, next_line]
                        if line is not None]

    bbox = get_bounding_box_for_lines(lines_to_include)

    # Vérifier que la bbox est dans les limites de l'image
    img_width, img_height = image.size
    bbox = (
        max(0, min(bbox[0], img_width)),
        max(0, min(bbox[1], img_height)),
        max(0, min(bbox[2], img_width)),
        max(0, min(bbox[3], img_height))
    )

    new_image = image.crop(bbox)
    buffered = BytesIO()
    new_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str