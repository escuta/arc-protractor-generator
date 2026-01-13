#!/usr/bin/env python3
"""
Arc Protractor Generator for Turntable Tonearms

Generates precision arc protractors for cartridge alignment based on 
tonearm mounting geometry and alignment standards (Baerwald, Löfgren B, Stevenson).

Author: Generated for turntable alignment
License: Public Domain
"""

import argparse
import math
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, letter

# Standard alignment geometries (IEC groove radii: 60.325mm inner, 146.05mm outer)
ALIGNMENTS = {
    'baerwald': {
        'name': 'Baerwald (Löfgren A)',
        'description': 'Minimizes maximum tracking error across the record',
        'inner_groove': 60.325,
        'outer_groove': 146.05,
        'null_formula': 'baerwald'
    },
    'lofgren_b': {
        'name': 'Löfgren B',
        'description': 'Minimizes RMS tracking error across the record',
        'inner_groove': 60.325,
        'outer_groove': 146.05,
        'null_formula': 'lofgren_b'
    },
    'stevenson': {
        'name': 'Stevenson',
        'description': 'Minimizes tracking error at inner grooves',
        'inner_groove': 60.325,
        'outer_groove': 146.05,
        'null_formula': 'stevenson'
    }
}

def calculate_effective_length_from_nulls(pivot_to_spindle, inner_null, outer_null):
    """
    Calculate effective length from null points using geometric analysis.
    
    Uses the relationship derived from the constraint that tracking error = 0
    at both null points. The formula L² = d² + r₁·r₂ (Bauer's approximation)
    is very accurate for most tonearm geometries.
    
    Args:
        pivot_to_spindle: Distance from pivot to spindle (mm)
        inner_null: Inner null point radius (mm)
        outer_null: Outer null point radius (mm)
    
    Returns:
        tuple: (effective_length, overhang, offset_angle, tracking_angle_midpoint)
    """
    
    d = pivot_to_spindle
    r1 = inner_null
    r2 = outer_null
    
    # Bauer's formula - gives excellent results
    effective_length = math.sqrt(d**2 + r1 * r2)
    overhang = effective_length - d
    
    # Calculate offset angle using the standard approximation
    # β ≈ arcsin((r₂ - r₁) / (2L))
    # This is the geometric angle between cartridge and tonearm tube
    offset_angle = math.degrees(math.asin((r2 - r1) / (2 * effective_length)))
    
    # Calculate tracking angle at midpoint (what VinylEngine calls "offset angle")
    # This is the angle at the average radius between null points
    r_midpoint = (r1 + r2) / 2
    tracking_angle_midpoint = math.degrees(math.asin(r_midpoint / effective_length))
    
    return effective_length, overhang, offset_angle, tracking_angle_midpoint


def calculate_null_points(pivot_to_spindle, alignment_type='baerwald', 
                         inner_groove=60.325, outer_groove=146.05):
    """
    Calculate null points based on alignment geometry and groove radii.
    
    For IEC standard groove radii (60.325, 146.05), this returns the established 
    optimal null point values. For other groove radii, it scales the null points
    proportionally while preserving the distortion balance characteristics of each
    alignment geometry.
    
    The scaling uses the square root of the groove range ratio to maintain the
    geometric relationships that define each alignment type's tracking error profile.
    
    Args:
        pivot_to_spindle: Distance from tonearm pivot to spindle center (mm)
        alignment_type: 'baerwald', 'lofgren_b', or 'stevenson'
        inner_groove: Innermost groove radius (mm)  
        outer_groove: Outermost groove radius (mm)
    
    Returns:
        tuple: (inner_null, outer_null, effective_length, overhang, offset_angle, tracking_angle_midpoint)
    """
    
    r_i = inner_groove
    r_o = outer_groove
    d = pivot_to_spindle
    
    # IEC standard reference values
    IEC_INNER = 60.325
    IEC_OUTER = 146.05
    
    if alignment_type == 'baerwald':
        # Baerwald (Löfgren A): Minimizes maximum tracking error
        # IEC standard null points
        IEC_N1 = 66.04
        IEC_N2 = 120.90
        
        # For IEC standard grooves, use exact values
        if abs(r_i - IEC_INNER) < 0.01 and abs(r_o - IEC_OUTER) < 0.01:
            inner_null = IEC_N1
            outer_null = IEC_N2
        else:
            # Scale null points proportionally for non-standard groove radii
            # This preserves the distortion balance characteristics
            scale_factor = math.sqrt((r_o - r_i) / (IEC_OUTER - IEC_INNER))
            offset_inner = IEC_N1 - IEC_INNER
            offset_outer = IEC_OUTER - IEC_N2
            
            inner_null = r_i + offset_inner * scale_factor
            outer_null = r_o - offset_outer * scale_factor
        
    elif alignment_type == 'lofgren_b':
        # Löfgren B: Minimizes RMS (average) tracking error
        # IEC standard null points
        IEC_N1 = 70.29
        IEC_N2 = 116.60
        
        # For IEC standard grooves, use exact values
        if abs(r_i - IEC_INNER) < 0.01 and abs(r_o - IEC_OUTER) < 0.01:
            inner_null = IEC_N1
            outer_null = IEC_N2
        else:
            # Scale null points proportionally for non-standard groove radii
            scale_factor = math.sqrt((r_o - r_i) / (IEC_OUTER - IEC_INNER))
            offset_inner = IEC_N1 - IEC_INNER
            offset_outer = IEC_OUTER - IEC_N2
            
            inner_null = r_i + offset_inner * scale_factor
            outer_null = r_o - offset_outer * scale_factor
        
    elif alignment_type == 'stevenson':
        # Stevenson: Inner null at innermost groove
        # Prioritizes low distortion at inner grooves
        inner_null = r_i
        
        # For IEC standard grooves, use known optimal value
        if abs(r_i - IEC_INNER) < 0.01 and abs(r_o - IEC_OUTER) < 0.01:
            outer_null = 117.42
        else:
            # For non-standard grooves, use geometric mean approximation
            outer_null = math.sqrt(r_i * r_o)
    
    else:
        raise ValueError(f"Unknown alignment type: {alignment_type}")
    
    # Calculate effective length from mounting distance and null points
    # Using Bauer's formula: L = sqrt(d² + x₁·x₂)
    # where x₁ and x₂ are the null point radii
    effective_length = math.sqrt(d**2 + inner_null * outer_null)
    
    # Overhang is the difference
    overhang = effective_length - d
    
    # Calculate offset angle
    # The offset angle is calculated using: β = arcsin((x₂ - x₁) / (2·L))
    # This is the angle between the cartridge centerline and the pivot-to-spindle line
    offset_angle = math.degrees(math.asin((outer_null - inner_null) / (2 * effective_length)))
    
    # Calculate tracking angle at midpoint (VinylEngine's "offset angle")
    r_midpoint = (inner_null + outer_null) / 2
    tracking_angle_midpoint = math.degrees(math.asin(r_midpoint / effective_length))
    
    return inner_null, outer_null, effective_length, overhang, offset_angle, tracking_angle_midpoint

def draw_arc_protractor(pivot_to_spindle, alignment='baerwald', 
                       output_file=None, custom_nulls=None,
                       inner_groove=60.325, outer_groove=146.05, custom_name=None,
                       papersize='A4'):
    """
    Generate arc protractor PDF.
    
    Args:
        pivot_to_spindle: Distance from pivot to spindle (mm)
        alignment: Alignment type ('baerwald', 'lofgren_b', 'stevenson')
        output_file: Output PDF filename
        custom_nulls: Tuple of (inner_null, outer_null) to override calculation
        inner_groove: Inner groove radius (mm)
        outer_groove: Outer groove radius (mm)
        custom_name: Custom name/description for the protractor
        papersize: Paper size ('A4', 'US', or 'letter')
    """
    
    if custom_nulls:
        inner_null, outer_null = custom_nulls
        
        # Validate null points are within valid ranges
        if inner_null <= inner_groove:
            raise ValueError(f"Inner null point ({inner_null:.2f}mm) must be greater than inner groove radius ({inner_groove:.2f}mm)")
        
        if outer_null >= outer_groove:
            raise ValueError(f"Outer null point ({outer_null:.2f}mm) must be less than outer groove radius ({outer_groove:.2f}mm)")
        
        if inner_null >= outer_null:
            raise ValueError(f"Inner null point ({inner_null:.2f}mm) must be less than outer null point ({outer_null:.2f}mm)")
        
        # Use proper geometric solver
        effective_length, overhang, offset_angle, tracking_angle_midpoint = \
            calculate_effective_length_from_nulls(pivot_to_spindle, inner_null, outer_null)
        alignment_name = f"Custom ({inner_null:.2f}/{outer_null:.2f}mm)"
    else:
        inner_null, outer_null, effective_length, overhang, offset_angle, tracking_angle_midpoint = \
            calculate_null_points(pivot_to_spindle, alignment, inner_groove, outer_groove)
        alignment_name = ALIGNMENTS[alignment]['name']
        
        # Validate that calculated null points are within valid ranges
        # Note: Stevenson alignment allows inner_null == inner_groove by design
        # Use small tolerance for floating point comparison
        tolerance = 0.001  # 1 micron tolerance
        
        if inner_null < (inner_groove - tolerance):
            raise ValueError(f"Calculated inner null point ({inner_null:.2f}mm) is less than inner groove radius ({inner_groove:.2f}mm). "
                           f"This geometry may not be suitable for {alignment_name} alignment with these groove dimensions.")
        
        if outer_null >= outer_groove:
            raise ValueError(f"Calculated outer null point ({outer_null:.2f}mm) is not less than outer groove radius ({outer_groove:.2f}mm). "
                           f"This geometry may not be suitable for {alignment_name} alignment with these groove dimensions.")
        
        if inner_null >= outer_null:
            raise ValueError(f"Calculated inner null point ({inner_null:.2f}mm) is not less than outer null point ({outer_null:.2f}mm). "
                           f"This is an invalid geometry - please check your pivot-to-spindle distance and groove dimensions.")
    
    # Set output filename
    if output_file is None:
        if custom_name:
            # Use custom name for filename (sanitize for filesystem)
            safe_name = custom_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            # Remove special characters that might cause issues
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
            output_file = f"{safe_name}.pdf"
        else:
            # Default filename
            output_file = "arc_protractor.pdf"
    
    # Select page size
    if papersize.upper() == 'A4':
        pagesize_to_use = A4
    elif papersize.upper() in ('US', 'LETTER'):
        pagesize_to_use = letter
    else:
        pagesize_to_use = A4  # Default fallback
    
    # Create PDF
    c = canvas.Canvas(output_file, pagesize=pagesize_to_use)
    width, height = pagesize_to_use
    
    # NEW ORIENTATION: Spindle at TOP, arc extending DOWNWARD
    # This is more intuitive - matches how tonearm actually moves
    
    # Position origin (spindle) near top of page - MOVED 1cm RIGHT
    origin_x = 65 * mm  # Moved 1cm right (reduced from 2cm)
    origin_y = height - 60*mm + 5*mm  # 55mm from top (raised by 0.5cm)
    
    # Text column on right side (UNCHANGED - text stays in place)
    text_start_x = 125*mm  # Right column for all text
    
    # Title and specs at top
    # Align titles with Data text on left side
    title_left_x = 20*mm  # Aligned with data_x
    
    # Align top of "Arc Protractor" with top of scissors (height - 20mm)
    # Font size 16 has approximately 5.6mm height, so baseline should be ~5.6mm below top
    title_baseline_y = height - 20*mm - 5.6*mm  # Approximately height - 25.6mm
    
    if custom_name:
        # Custom name: "Arc Protractor" on first line, name on second line
        c.setFont("Helvetica-Bold", 16)
        c.drawString(title_left_x, title_baseline_y, "Arc Protractor")
        
        # Reduced spacing: 8mm between lines (was 12mm)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(title_left_x, title_baseline_y - 8*mm, custom_name)
        
        # Show alignment type smaller below with 6mm spacing
        c.setFont("Helvetica", 9)
        c.drawString(title_left_x, title_baseline_y - 14*mm, alignment_name)
    else:
        # Standard title - no custom name, so raise geometry name to second line position
        c.setFont("Helvetica-Bold", 16)
        c.drawString(title_left_x, title_baseline_y, "Arc Protractor")
        
        # Geometry name raised to where custom_name would be (8mm below instead of staying at third line)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(title_left_x, title_baseline_y - 8*mm, alignment_name)
    
    # Add vertical scissor icon and dashed cutting line to separate protractor from text
    # Position between the protractor area and text column
    # Current position: text_start_x - 2.5mm
    # Move 2cm right: text_start_x - 2.5mm + 20mm = text_start_x + 17.5mm
    cut_line_x = text_start_x + 17.5*mm
    
    # Draw scissor symbol at top of cutting line
    c.setFont("Helvetica", 16)
    # Original: height - 35mm
    # First adjustment: +20mm up
    # Second adjustment: -5mm down
    # Net: height - 35mm + 20mm - 5mm = height - 20mm
    scissor_y = height - 20*mm
    c.saveState()
    c.translate(cut_line_x, scissor_y)
    c.rotate(90)  # Rotate scissor 90 degrees for vertical cut
    c.drawString(-3*mm, -2*mm, "✂")
    c.restoreState()
    
    # Draw vertical dashed cutting line (quarter of the original length)
    # Original length was from height - 45mm to 20mm (total: height - 65mm)
    # Quarter length: (height - 65mm) / 4
    line_length = (height - 45*mm - 20*mm) / 4
    # First adjustment: +20mm up, Second: -5mm down = +15mm net
    line_start_y = height - 45*mm + 15*mm  # height - 30mm
    line_end_y = line_start_y - line_length
    
    c.setDash(3, 3)  # 3mm dash, 3mm gap
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)  # Gray color
    c.line(cut_line_x, line_start_y, cut_line_x, line_end_y)
    
    # Reset to solid line for rest of drawing
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)  # Back to black
    
    # Data section - moved to left side, beneath protractor
    # Position it lower to avoid overlap with protractor graphic
    data_x = 20*mm  # Left side, aligned with scale
    data_start_y = 90*mm  # Raised by 1cm (from 80mm to 90mm)
    
    # "Data" title in bold
    c.setFont("Helvetica-Bold", 9)
    c.drawString(data_x, data_start_y, "Data")
    
    # Specs with 4mm spacing between lines (reduced from 6mm)
    c.setFont("Helvetica", 9)
    c.drawString(data_x, data_start_y - 6*mm, f"Pivot to Spindle:")
    c.drawString(data_x + 40*mm, data_start_y - 6*mm, f"{pivot_to_spindle:.2f} mm")
    
    c.drawString(data_x, data_start_y - 10*mm, f"Effective Length:")
    c.drawString(data_x + 40*mm, data_start_y - 10*mm, f"{effective_length:.3f} mm")
    
    c.drawString(data_x, data_start_y - 14*mm, f"Overhang:")
    c.drawString(data_x + 40*mm, data_start_y - 14*mm, f"{overhang:.3f} mm")
    
    c.drawString(data_x, data_start_y - 18*mm, f"Inner Null Point:")
    c.drawString(data_x + 40*mm, data_start_y - 18*mm, f"{inner_null:.3f} mm")
    
    c.drawString(data_x, data_start_y - 22*mm, f"Outer Null Point:")
    c.drawString(data_x + 40*mm, data_start_y - 22*mm, f"{outer_null:.3f} mm")
    
    c.drawString(data_x, data_start_y - 26*mm, f"Groove Radii:")
    c.drawString(data_x + 40*mm, data_start_y - 26*mm, f"{inner_groove:.2f} - {outer_groove:.2f} mm")
    
    c.drawString(data_x, data_start_y - 30*mm, f"Mounting Angle:")
    mounting_str = f"{offset_angle:.3f}°"
    c.drawString(data_x + 40*mm, data_start_y - 30*mm, mounting_str)
    mounting_width = c.stringWidth(mounting_str, "Helvetica", 9)
    c.setFont("Helvetica", 7)
    c.drawString(data_x + 40*mm + mounting_width + 1.5*mm, data_start_y - 30*mm, f"(cartridge to arm)")
    c.setFont("Helvetica", 9)
    
    c.drawString(data_x, data_start_y - 34*mm, f"Offset Angle:")
    offset_str = f"{tracking_angle_midpoint:.3f}°"
    c.drawString(data_x + 40*mm, data_start_y - 34*mm, offset_str)
    offset_width = c.stringWidth(offset_str, "Helvetica", 9)
    c.setFont("Helvetica", 7)
    c.drawString(data_x + 40*mm + offset_width + 1.5*mm, data_start_y - 34*mm, f"(at midpoint)")
    c.setFont("Helvetica", 9)
    
    # Scale verification at BOTTOM LEFT (below data section)
    scale_x = 20*mm  # Left side
    
    # "100.0 mm" text position - raise by 0.5cm (from 7mm to 12mm)
    hundred_mm_y = 12*mm
    
    # Scale bar should be 10mm above the "100.0 mm" text
    scale_y = hundred_mm_y + 10*mm  # 22mm from bottom
    
    # Verification text - 5mm above scale bar
    c.setFont("Helvetica", 9)
    c.drawString(scale_x, scale_y + 5*mm, "Scale verification. This bar must measure exactly:")
    
    # 100mm scale bar
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.6)
    c.line(scale_x, scale_y, scale_x + 100*mm, scale_y)
    c.line(scale_x, scale_y - 3*mm, scale_x, scale_y + 3*mm)
    c.line(scale_x + 100*mm, scale_y - 3*mm, scale_x + 100*mm, scale_y + 3*mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(scale_x + 37*mm, hundred_mm_y, "100.0 mm")
    
    # Move to working area - spindle position on left side of page
    c.translate(origin_x, origin_y)
    
    # Draw spindle hole (7mm diameter for record spindle)
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3)
    c.circle(0, 0, 3.5*mm, stroke=1, fill=0)
    
    # Draw crosshair at spindle
    c.setLineWidth(0.2)
    c.line(-5*mm, 0, 5*mm, 0)
    c.line(0, -5*mm, 0, 5*mm)
    
    # Spindle label - vertically centered on spindle center
    c.setFont("Helvetica-Bold", 9)
    # Font size 9 has approximately 3.2mm height, so offset by half to center
    c.drawString(6*mm, -1.6*mm, "Spindle")
    
    # Calculate pivot point position - RIGHT side for normal turntables
    pivot_x = pivot_to_spindle * mm  # POSITIVE = to the right
    pivot_y = 0
    
    # Draw pivot point marker - BLACK not red
    c.setStrokeColorRGB(0, 0, 0)  # Black (was red)
    c.circle(pivot_x, pivot_y, 2*mm, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(pivot_x + 4*mm, pivot_y + 4*mm, "PIVOT")
    c.setFont("Helvetica", 7)
    c.drawString(pivot_x + 4*mm, pivot_y - 5*mm, f"{pivot_to_spindle:.1f}mm")
    
    # Arc will be drawn LAST (after grids) so it's visible on top
    arc_radius = effective_length * mm
    
    # Draw alignment grids at null points (NOW BELOW SPINDLE, LEFT OF PIVOT)
    def draw_alignment_grid(radius_from_spindle, label):
        # Calculate position of null point
        # Null point is at intersection of:
        # 1. Circle centered at spindle (0,0) with radius = radius_from_spindle
        # 2. Circle centered at pivot with radius = effective_length
        #
        # Solving: x² + y² = r₁²
        #          (x - d)² + y² = r₂²
        # Where r₁ = radius_from_spindle, r₂ = effective_length, d = pivot_to_spindle
        #
        # x = (d² + r₁² - r₂²) / (2d)
        # y = -sqrt(r₁² - x²)  [negative for below spindle]
        
        r1 = radius_from_spindle * mm
        r2 = arc_radius
        d = pivot_x
        
        x_pos = (d**2 + r1**2 - r2**2) / (2 * d)
        y_pos = -math.sqrt(r1**2 - x_pos**2)  # Below spindle
        
        # Calculate grid angle from groove geometry
        # At null point: stylus must track tangent to groove (zero tracking error)
        # Groove = circle centered at SPINDLE
        #
        # Radius from spindle: (x_pos, y_pos)
        # Clockwise tangent (for clockwise record rotation): (y_pos, -x_pos)
        
        groove_tangent_x = y_pos
        groove_tangent_y = -x_pos
        grid_angle = math.degrees(math.atan2(groove_tangent_y, groove_tangent_x))
        
        # Draw filled dot for stylus positioning (BEFORE rotating)
        c.setStrokeColorRGB(0, 0, 0)  # Black
        c.setFillColorRGB(0, 0, 0)    # Black fill
        c.setLineWidth(0.3)
        # Small filled circle at exact stylus position - 1mm diameter
        c.circle(x_pos, y_pos, 0.5*mm, stroke=1, fill=1)
        
        # Draw grid for cartridge alignment - BLACK not blue
        c.setStrokeColorRGB(0, 0, 0)  # Black (was blue)
        c.setLineWidth(0.4)
        
        c.saveState()
        c.translate(x_pos, y_pos)
        c.rotate(grid_angle)
        
        # Grid extends 1.5cm in NEGATIVE x direction (which points toward pivot in page coords)
        # Due to rotation, negative x in rotated frame points toward arm on page
        grid_left = -30*mm  # 15mm base + 15mm extension toward arm
        grid_right = 15*mm  # 15mm base only
        grid_spacing = 2*mm
        
        # Horizontal lines
        for i in range(-4, 5):
            y = i * grid_spacing
            c.setLineWidth(0.3 if i == 0 else 0.2)
            c.line(grid_left, y, grid_right, y)
        
        # Draw perpendicular center line - symmetric, not extended
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)  # Black (was red)
        # Keep perpendicular line symmetric and shorter
        perp_half = 15*mm
        c.line(0, -perp_half, 0, perp_half)
        
        c.restoreState()
        
        # Draw labels rotated to match grid angle
        # Position to the LEFT of grid with clearance
        c.setStrokeColorRGB(0, 0, 0)
        
        # Grid is 30mm wide (15mm each side from center)
        # Add 3mm clearance beyond grid edge = 18mm from center
        label_x = x_pos - 18*mm
        label_y = y_pos
        
        # Normalize grid angle to keep text readable (not upside down)
        # Text readable when angle between -90° and +90°
        label_angle = grid_angle
        while label_angle > 90:
            label_angle -= 180
        while label_angle < -90:
            label_angle += 180
        
        # Don't negate - use normalized angle directly
        
        c.saveState()
        c.translate(label_x, label_y)
        c.rotate(label_angle)  # Rotate to match grid
        
        # Draw text at origin (after rotation and translation)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(0, 1*mm, label)
        c.setFont("Helvetica", 8)
        c.drawRightString(0, -3*mm, f"{radius_from_spindle:.2f}mm")
        
        c.restoreState()
    
    # Draw diagnostic radius lines FIRST (so grids render on top with full black color)
    # These help verify that grids are perpendicular to spindle radius
    # Radial lines to null points
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3)
    
    # Helper function to calculate null point position
    def calc_null_position(radius_from_spindle):
        r1 = radius_from_spindle * mm
        r2 = arc_radius
        d = pivot_x
        x = (d**2 + r1**2 - r2**2) / (2 * d)
        y = -math.sqrt(r1**2 - x**2)
        return x, y
    
    # Inner null radius line
    x_inner, y_inner = calc_null_position(inner_null)
    c.line(0, 0, x_inner, y_inner)
    
    # Outer null radius line
    x_outer, y_outer = calc_null_position(outer_null)
    c.line(0, 0, x_outer, y_outer)
    
    # Draw grids at both null points (AFTER radius lines so they stay black)
    draw_alignment_grid(inner_null, "Inner Null Point")
    draw_alignment_grid(outer_null, "Outer Null Point")
    
    # Draw arc LAST so it's visible on top of everything
    # Arc should START 4cm above inner null (closer to spindle)
    # and END 4cm below outer null (further from spindle)
    def calc_arc_angle(radius_from_spindle):
        r1 = radius_from_spindle * mm
        r2 = arc_radius
        d = pivot_x
        
        # Check if valid - radius_from_spindle in mm, need to check physical limits
        # Circles must be able to intersect
        if radius_from_spindle < 0 or radius_from_spindle > 200:  # Reasonable bounds
            return None
        
        # Calculate intersection point
        x = (d**2 + r1**2 - r2**2) / (2 * d)
        y_squared = r1**2 - x**2
        
        if y_squared < 0:
            return None
        
        y = -math.sqrt(y_squared)
        
        # Angle from pivot to this point
        angle = math.degrees(math.atan2(y - pivot_y, x - pivot_x))
        if angle < 0:
            angle += 360
        return angle
    
    # Calculate radii: try 4cm extension beyond each null point
    # For extreme geometries (like Stevenson), reduce extension if needed
    target_extension = 40  # 4cm in mm
    
    # Try extending the arc
    arc_start_radius = inner_null - target_extension
    arc_end_radius = outer_null + target_extension
    
    # Check if geometry is valid, reduce extension if needed
    start_test = calc_arc_angle(arc_start_radius)
    
    # If inner extension fails, reduce it until it works
    if start_test is None:
        # Binary search for maximum valid extension
        for extension in range(target_extension, 0, -1):
            arc_start_radius = inner_null - extension
            if calc_arc_angle(arc_start_radius) is not None:
                break
        else:
            # No extension possible, use inner null itself
            arc_start_radius = inner_null
    
    # Similarly check outer extension
    end_test = calc_arc_angle(arc_end_radius)
    if end_test is None:
        for extension in range(target_extension, 0, -1):
            arc_end_radius = outer_null + extension
            if calc_arc_angle(arc_end_radius) is not None:
                break
        else:
            arc_end_radius = outer_null
    
    # Now calculate the actual angles
    start_angle = calc_arc_angle(arc_start_radius)
    end_angle = calc_arc_angle(arc_end_radius)
    
    # Draw stylus arc (should always work now)
    if start_angle is not None and end_angle is not None:
        # Calculate extent (reportlab wants startAng, extent - NOT two angles!)
        extent = end_angle - start_angle
        
        # Draw stylus arc
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.3)
        c.arc(pivot_x - arc_radius, pivot_y - arc_radius, 
              pivot_x + arc_radius, pivot_y + arc_radius,
              start_angle, extent)
    
    c.save()
    
    return output_file, {
        'pivot_to_spindle': pivot_to_spindle,
        'effective_length': effective_length,
        'overhang': overhang,
        'inner_null': inner_null,
        'outer_null': outer_null,
        'offset_angle': offset_angle,
        'tracking_angle_midpoint': tracking_angle_midpoint
    }

def main():
    parser = argparse.ArgumentParser(
        description='Generate arc protractor for turntable cartridge alignment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SME 3009 S2 Improved with Baerwald alignment (A4 paper)
  %(prog)s 215.5

  # Same tonearm with US Letter paper
  %(prog)s 215.5 --papersize US

  # Löfgren B alignment
  %(prog)s 215.5 --alignment lofgren_b

  # Technics SL-1200 with Stevenson alignment
  %(prog)s 215.0 --alignment stevenson -o technics_protractor.pdf

  # Custom null points
  %(prog)s 215.5 --custom-nulls 66.0 120.9

  # Show what each alignment calculates
  %(prog)s 215.5 --show-all

Common tonearm mounting distances:
  SME 3009 S2 Improved (early):   215.5-215.7 mm
  SME 3009 S2 Improved (late):    213.25 mm
  Technics SL-1200:               215.0 mm
  Rega RB300:                     222.0 mm
  Audio-Technica AT-LP120:        215.0 mm
  Pro-Ject 8.6" tonearms:         200.0 mm
        """
    )
    
    parser.add_argument('pivot_to_spindle', type=float,
                       help='Distance from tonearm pivot to spindle center (mm)')
    
    parser.add_argument('-a', '--alignment', 
                       choices=['baerwald', 'lofgren_b', 'stevenson'],
                       default='baerwald',
                       help='Alignment geometry (default: baerwald)')
    
    parser.add_argument('-o', '--output',
                       help='Output PDF filename (default: auto-generated)')
    
    parser.add_argument('--custom-nulls', nargs=2, type=float,
                       metavar=('INNER', 'OUTER'),
                       help='Custom null points in mm (overrides alignment type)')
    
    parser.add_argument('--inner-groove', type=float, default=60.325,
                       help='Inner groove radius in mm (default: 60.325 IEC)')
    
    parser.add_argument('--outer-groove', type=float, default=146.05,
                       help='Outer groove radius in mm (default: 146.05 IEC)')
    
    parser.add_argument('--show-all', action='store_true',
                       help='Show calculations for all alignment types and exit')
    
    parser.add_argument('--name', type=str,
                       help='Custom name/description for the protractor. '
                            'Used as title and filename if -o not specified. '
                            'Example: --name "SME 3009 S2 Improved Serial 23123"')
    
    parser.add_argument('--papersize', 
                       choices=['A4', 'US', 'letter'],
                       default='A4',
                       help='Paper size: A4 (210x297mm) or US/letter (8.5x11in) (default: A4)')
    
    args = parser.parse_args()
    
    # Show all alignments if requested
    if args.show_all:
        print(f"\nAlignment calculations for {args.pivot_to_spindle}mm mounting distance:")
        print(f"Groove radii: {args.inner_groove:.2f} - {args.outer_groove:.2f}mm\n")
        print(f"{'Alignment':<20} {'Inner Null':<12} {'Outer Null':<12} {'Eff. Length':<13} {'Overhang':<10} {'Mount°':<9} {'Offset°'}")
        print("-" * 105)
        
        for alignment_key in ['baerwald', 'lofgren_b', 'stevenson']:
            inner_null, outer_null, eff_len, overhang, mounting, offset = \
                calculate_null_points(args.pivot_to_spindle, alignment_key, 
                                     args.inner_groove, args.outer_groove)
            name = ALIGNMENTS[alignment_key]['name']
            print(f"{name:<20} {inner_null:>10.3f}mm {outer_null:>10.3f}mm {eff_len:>11.3f}mm {overhang:>8.3f}mm {mounting:>7.3f} {offset:>7.3f}")
        print()
        return
    
    # Generate protractor
    try:
        output_file, specs = draw_arc_protractor(
            args.pivot_to_spindle,
            alignment=args.alignment,
            output_file=args.output,
            custom_nulls=tuple(args.custom_nulls) if args.custom_nulls else None,
            inner_groove=args.inner_groove,
            outer_groove=args.outer_groove,
            custom_name=args.name,
            papersize=args.papersize
        )
        
        print(f"\n✓ Protractor generated successfully!")
        print(f"  File: {output_file}\n")
        print("Specifications:")
        print(f"  Pivot to Spindle: {specs['pivot_to_spindle']:.3f} mm")
        print(f"  Effective Length:  {specs['effective_length']:.3f} mm")
        print(f"  Overhang:          {specs['overhang']:.3f} mm")
        print(f"  Inner Null Point:  {specs['inner_null']:.3f} mm")
        print(f"  Outer Null Point:  {specs['outer_null']:.3f} mm")
        print(f"  Mounting Angle:    {specs['offset_angle']:.3f}° (cartridge to arm)")
        print(f"  Offset Angle:      {specs['tracking_angle_midpoint']:.3f}° (at midpoint)")
        print("\n⚠  IMPORTANT: Print at 100% scale and verify measurements!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
