"""
PDF to DXF Converter (PyMuPDF Edition)
=======================================
Because installing Poppler feels like a side quest you didn’t sign up for.
This script uses PyMuPDF to read PDFs and ezdxf to create DXF files.
Warning: May cause CAD users to smile awkwardly.
"""

import fitz  # PyMuPDF
import ezdxf

def pdf_to_dxf(pdf_path, dxf_path):
    """
    Converts a PDF into a DXF file using PyMuPDF for vector extraction.
    
    Parameters:
    pdf_path (str): Path to the PDF file.
    dxf_path (str): Path to save the DXF file.
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Create a new DXF document
    dxf_doc = ezdxf.new()
    msp = dxf_doc.modelspace()
    
    # Loop through pages
    for page_num, page in enumerate(doc):
        print(f"Processing page {page_num + 1}...")
        
        # Extract vector drawings
        drawings = page.get_drawings()
        for d in drawings:
            for item in d["items"]:
                if item[0] == "l":  # line
                    _, p1, p2, *_ = item
                    msp.add_line(p1, p2)
                elif item[0] == "re":  # rectangle
                    _, rect, *_ = item
                    msp.add_lwpolyline([(rect.x0, rect.y0), (rect.x1, rect.y0),
                                        (rect.x1, rect.y1), (rect.x0, rect.y1)], close=True)
        
        # Extract text (optional)
        text_instances = page.get_text("blocks")
        for block in text_instances:
            x, y, _, _, text, *_ = block
            msp.add_text(text, dxfattribs={"height": 2.5}).set_pos((x, y))
    
    # Save DXF
    dxf_doc.saveas(dxf_path)
    print(f"DXF saved at: {dxf_path}")

# Example usage:
pdf_to_dxf("input.pdf", "output.dxf")
