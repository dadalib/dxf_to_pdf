
"""
Enhanced PDF to DXF Converter (PyMuPDF + ezdxf)
================================================
Supports lines, rectangles, circles, polygons, Bezier curves, and text.
Includes safe path handling and automatic folder creation.
"""

import fitz  # PyMuPDF
import ezdxf
from pathlib import Path
import os

def pdf_to_dxf(pdf_path, dxf_path, scale=1.0):
    """
    Converts a PDF into a DXF file using PyMuPDF for vector extraction.
    
    Parameters:
        pdf_path (str or Path): Path to the PDF file.
        dxf_path (str or Path): Path to save the DXF file.
        scale (float): Scaling factor for coordinates (default = 1.0).
    """
    # Normalise paths
    pdf_path = Path(pdf_path).resolve()
    dxf_path = Path(dxf_path).resolve()

    # Ensure output directory exists
    os.makedirs(dxf_path.parent, exist_ok=True)

    # Open the PDF
    doc = fitz.open(str(pdf_path))

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
                t = item[0]
                
                if t == "l":  # line
                    _, p1, p2, *_ = item
                    msp.add_line((p1[0]*scale, p1[1]*scale), (p2[0]*scale, p2[1]*scale))
                
                elif t == "re":  # rectangle
                    _, rect, *_ = item
                    msp.add_lwpolyline([
                        (rect.x0*scale, rect.y0*scale),
                        (rect.x1*scale, rect.y0*scale),
                        (rect.x1*scale, rect.y1*scale),
                        (rect.x0*scale, rect.y1*scale)
                    ], close=True)
                
                elif t == "c":  # circle
                    _, center, point_on_circle, *_ = item
                    # Calculate radius from two points
                    radius = ((point_on_circle[0] - center[0])**2 + (point_on_circle[1] - center[1])**2) ** 0.5
                    msp.add_circle((center[0]*scale, center[1]*scale), radius*scale)
                
                elif t == "p":  # polygon
                    _, points, *_ = item
                    scaled_points = [(x*scale, y*scale) for x, y in points]
                    msp.add_lwpolyline(scaled_points, close=True)
                
                elif t == "b":  # bezier curve
                    _, points, *_ = item
                    scaled_points = [(x*scale, y*scale) for x, y in points]
                    msp.add_spline(scaled_points)

        # Extract text blocks
        text_instances = page.get_text("blocks")
        for block in text_instances:
            x, y, _, _, text, *_ = block
            msp.add_text(text, dxfattribs={"height": 2.5}).set_pos((x*scale, y*scale))

    # Save DXF
    dxf_doc.saveas(str(dxf_path))
    print(f"DXF saved at: {dxf_path}")

# Example usage:
pdf_to_dxf("C:/Users/lida/Projects/python_playlist/dxf_to_pdf/input.pdf", "C:/Users/lida/Projects/python_playlist/dxf_to_pdf/output.dxf", scale=1.0)
