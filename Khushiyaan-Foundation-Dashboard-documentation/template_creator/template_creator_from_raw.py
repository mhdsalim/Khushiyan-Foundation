from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter

def create_static_template(output_path):
    # Load static logos
    left_logo = ImageReader("assets/Khushiyaan Logo.jpg")
    right_logo = ImageReader("template_creator/sponsor_logo.jpg")

    temp_pdf = "overlay.pdf"
    c = canvas.Canvas(temp_pdf)

    # ----- PLACE LOGOS -----
    # Standard width for BOTH logos
    # ----- PLACE LOGOS -----
    LOGO_WIDTH = 180
    TOP_Y = 705
    GAP = 1   # spacing between the two logos

    # Khushiyaan logo – TOP
    c.drawImage(left_logo, 8, TOP_Y, width=LOGO_WIDTH, preserveAspectRatio=True, mask='auto')

    # Legrand logo – BELOW it
    second_logo_y = TOP_Y - 300 
    c.drawImage(right_logo, 8, second_logo_y, width=LOGO_WIDTH, preserveAspectRatio=True, mask='auto')

    


    c.save()
    template_path = "template_creator/raw_template.pdf"
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

# Run once
create_static_template("assets/base_template.pdf")
