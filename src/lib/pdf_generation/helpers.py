from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors

NAMETAG_FONT_PATH =  __file__.replace("lib/pdf_generation/helpers.py", '') + "data/Trebuchet.ttf"

# Add String text to label at (width, height). Font_size gets adjusted to max_width
# You can add a max_font_size where the calculation starts
def add_text_field(label, text, width, height, max_width=-1, max_font_size=100, font_size=-1, font = "Trebuchet", color=colors.black, position="middle"):
    if max_width == -1:
        max_width = width

    if font_size == -1:
        while stringWidth(text, font, max_font_size) > max_width:
            max_font_size *= 0.9
        font_size = max_font_size

    s = shapes.String(width, height, text, textAnchor=position)
    s.fontName = font
    s.fontSize = font_size
    s.fillColor = color
    label.add(s)