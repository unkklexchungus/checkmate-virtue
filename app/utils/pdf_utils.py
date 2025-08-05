"""
PDF generation utilities.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import settings


def generate_inspection_pdf(inspection: Dict[str, Any]) -> Path:
    """Generate PDF report for inspection."""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".pdf", 
        delete=False, 
        dir=settings.PDF_TEMP_DIR
    )
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        temp_file.name,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Build story
    story = []
    
    # Title
    title = Paragraph(f"Inspection Report: {inspection.get('title', 'Untitled')}", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Inspection details
    story.extend(_create_inspection_details(inspection))
    story.append(Spacer(1, 20))
    
    # Categories and items
    story.extend(_create_categories_section(inspection))
    
    # Build PDF
    doc.build(story)
    
    return Path(temp_file.name)


def _create_inspection_details(inspection: Dict[str, Any]) -> list:
    """Create inspection details section."""
    story = []
    
    # Basic info
    data = [
        ["Inspector:", inspection.get('inspector_name', 'N/A')],
        ["Inspector ID:", inspection.get('inspector_id', 'N/A')],
        ["Date:", inspection.get('date', 'N/A')],
        ["Status:", inspection.get('status', 'N/A')],
    ]
    
    # Industry info
    industry_info = inspection.get('industry_info', {})
    if industry_info:
        data.extend([
            ["Industry Type:", industry_info.get('industry_type', 'N/A')],
            ["Facility:", industry_info.get('facility_name', 'N/A')],
            ["Location:", industry_info.get('location', 'N/A')],
            ["Contact:", industry_info.get('contact_person', 'N/A')],
            ["Phone:", industry_info.get('phone', 'N/A')],
        ])
    
    # Vehicle info (if automotive)
    vehicle_info = inspection.get('vehicle_info')
    if vehicle_info:
        data.extend([
            ["Vehicle Year:", vehicle_info.get('year', 'N/A')],
            ["Make:", vehicle_info.get('make', 'N/A')],
            ["Model:", vehicle_info.get('model', 'N/A')],
            ["VIN:", vehicle_info.get('vin', 'N/A')],
            ["License Plate:", vehicle_info.get('license_plate', 'N/A')],
            ["Mileage:", vehicle_info.get('mileage', 'N/A')],
        ])
    
    # Create table
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    return story


def _create_categories_section(inspection: Dict[str, Any]) -> list:
    """Create categories and items section."""
    story = []
    
    categories = inspection.get('categories', [])
    if not categories:
        story.append(Paragraph("No inspection items found.", getSampleStyleSheet()['Normal']))
        return story
    
    for category in categories:
        # Category header
        category_style = ParagraphStyle(
            'CategoryHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20
        )
        story.append(Paragraph(f"Category: {category.get('name', 'Unnamed')}", category_style))
        
        # Category description
        if category.get('description'):
            story.append(Paragraph(category['description'], getSampleStyleSheet()['Normal']))
            story.append(Spacer(1, 12))
        
        # Items table
        items = category.get('items', [])
        if items:
            story.extend(_create_items_table(items))
        
        story.append(Spacer(1, 20))
    
    return story


def _create_items_table(items: list) -> list:
    """Create items table."""
    story = []
    
    # Table headers
    data = [["Item", "Grade", "Notes"]]
    
    # Add items
    for item in items:
        data.append([
            item.get('name', 'Unnamed'),
            item.get('grade', 'N/A'),
            item.get('notes', '')[:100] + '...' if len(item.get('notes', '')) > 100 else item.get('notes', '')
        ])
    
    # Create table
    table = Table(data, colWidths=[2*inch, 1*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    return story 