from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os
import io
import requests

def format_title(text):
    return text.title().strip()

import requests
import io

def download_image_from_gdrive(url):
    """
    Downloads ANY image from Google Drive — even large files.
    Returns BytesIO buffer.
    """

    session = requests.Session()

    # Extract file ID
    if "drive.google.com" in url:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1]
        else:
            raise ValueError("Invalid Google Drive link")

        download_url = "https://drive.google.com/uc?export=download"
        response = session.get(download_url, params={"id": file_id}, stream=True)
    else:
        response = session.get(url, stream=True)

    # Google Drive sometimes returns a warning token for large files
    def get_confirm_token(res):
        for key, value in res.cookies.items():
            if key.startswith("download_warning"):
                return value
        return None

    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(download_url, params=params, stream=True)

    # Ensure we got an image, not HTML
    content_type = response.headers.get("Content-Type", "")
    if "image" not in content_type:
        raise ValueError("Google Drive did not return an image. Check sharing permissions.")

    buffer = io.BytesIO(response.content)
    buffer.seek(0)
    return buffer

def universal_to_jpg(input_data, quality=35, max_width=475, max_height=300):

    # Input can be path OR a BytesIO buffer
    if isinstance(input_data, io.BytesIO):
        img = Image.open(input_data)
    else:
        img = Image.open(str(input_data))

    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    return buffer


def generate_certificate(
    name,
    event_name,
    location,
    date,
    sponsor, 
    template_path,
    output_path,
    photo_path

):

    if photo_path.startswith("http"):
        raw_img = download_image_from_gdrive(photo_path)
        user_photo = universal_to_jpg(raw_img)
    else:
        user_photo = universal_to_jpg(photo_path)
    # ----- FORMAT TEXT -----
    name_text = name.upper().strip()
    event_text = format_title(event_name)
    location_text = format_title(location)
    date_text = date.strip()
    line_last = f"{location_text} on {date_text}"

    # ----- REGISTER FONTS -----
    pdfmetrics.registerFont(TTFont("Lora", "assets/Lora-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("Josefin", "assets/JosefinSans-Regular.ttf"))

    pdfmetrics.registerFont(TTFont("JosefinSans", "assets/JosefinSans-Light.ttf"))



    # ----- DRAW OVERLAY -----
    temp_pdf = "overlay.pdf"
    c = canvas.Canvas(temp_pdf)



    # ----- TEXT PLACEMENT -----
    PAGE_WIDTH = 595.5
    x = 100
    y = 450

    c.setFont("JosefinSans", 26)
    Text1 = "This award is presented to"
    width1 = pdfmetrics.stringWidth(Text1, "JosefinSans", 26)
    x_1 = (PAGE_WIDTH - width1) / 2
    c.drawString(x_1, y, Text1)
    y -= 45
    # NAME
    c.setFont("Lora", 26.5)
    name_width = pdfmetrics.stringWidth(name_text, "Lora", 26.5)
    name_x = (PAGE_WIDTH - name_width) / 2
    c.drawString(name_x, y, name_text)

    c.line(name_x, y - 5, name_x + name_width, y - 5)
    y -= 43

    # Paragraph
    c.setFont("Josefin", 20.6)
    if sponsor:
        paragraph_lines = [
            "For participating with enthusiasm at",
            f"{event_text} -",
            f"a social initiative by {sponsor} ",
            "and Khushiyaan Foundation at",
            line_last
        ]
    else:
        paragraph_lines = [
            "For participating with enthusiasm at",
            f"{event_text} -",
            f"a social initiative by Khushiyaan Foundation at ",
            line_last
        ]

    for line in paragraph_lines:
        width = pdfmetrics.stringWidth(line, "Josefin", 20.6)
        x = (PAGE_WIDTH - width) / 2
        c.drawString(x, y, line)
        y -= 28

    # ----- FADED CENTER BACKGROUND IMAGE -----
    user_photo = ImageReader(user_photo)
    try:
        c.saveState()
        c.setFillAlpha(0.18)  # fade level
    except:
        pass  # safe fallback
    width, height = user_photo.getSize()
    c.drawImage(
        user_photo,
        (PAGE_WIDTH -width)/2,
        210,
        height=300,
        preserveAspectRatio=True,
        mask='auto'
    )

    try:
        c.restoreState()
    except:
        pass
        
    c.save()

    # ----- MERGE WITH TEMPLATE -----
    template = PdfReader(template_path)
    overlay = PdfReader(temp_pdf)

    writer = PdfWriter()
    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print("✅ Certificate created:", output_path)
