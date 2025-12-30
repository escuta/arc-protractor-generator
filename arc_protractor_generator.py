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
        tuple: (effective_length, overhang, offset_angle)
    """
    
    d = pivot_to_spindle
    r1 = inner_null
    r2 = outer_null
    
    # Bauer's formula - gives excellent results
    effective_length = math.sqrt(d**2 + r1 * r2)
    overhang = effective_length - d
    
    # Calculate offset angle using the standard approximation
    # β ≈ arcsin((r₂ - r₁) / (2L))
    offset_angle = math.degrees(math.asin((r2 - r1) / (2 * effective_length)))
    
    return effective_length, overhang, offset_angle


def calculate_null_points(pivot_to_spindle, alignment_type='baerwald', 
                         inner_groove=60.325, outer_groove=146.05):
    """
    Calculate null points based on alignment geometry.
    
    For standard IEC groove radii (60.325, 146.05), this uses established 
    null point formulas. The effective length is then calculated from the
    mounting distance and null points.
    
    Args:
        pivot_to_spindle: Distance from tonearm pivot to spindle center (mm)
        alignment_type: 'baerwald', 'lofgren_b', or 'stevenson'
        inner_groove: Innermost groove radius (mm)  
        outer_groove: Outermost groove radius (mm)
    
    Returns:
        tuple: (inner_null, outer_null, effective_length, overhang, offset_angle)
    """
    
    r_i = inner_groove
    r_o = outer_groove
    d = pivot_to_spindle
    
    # Calculate null point radii for IEC standard groove dimensions
    # Note: These null points are optimized for IEC/RIAA standard (60.325-146.05mm)
    # Using different groove radii would require different optimization
    
    if alignment_type == 'baerwald':
        # Baerwald (Löfgren A): Minimizes maximum tracking error
        # Standard IEC null points (empirically derived optimal values)
        inner_null = 66.04
        outer_null = 120.90
        
    elif alignment_type == 'lofgren_b':
        # Löfgren B (DIN): Minimizes RMS tracking error  
        # Standard IEC null points
        inner_null = 70.29
        outer_null = 116.60
        
    elif alignment_type == 'stevenson':
        # Stevenson: Nulls at groove limits
        # Prioritizes low distortion at record end (outer groove)
        # Note: Some sources use modified Stevenson with different outer null
        inner_null = r_i  # At innermost groove
        outer_null = r_o  # At outermost groove
    
    else:
        raise ValueError(f"Unknown alignment type: {alignment_type}")
    
    # Calculate effective length from mounting distance and null points
    # Using the formula: L = sqrt(d² + x₁·x₂)
    # where x₁ and x₂ are the null point radii
    effective_length = math.sqrt(d**2 + inner_null * outer_null)
    
    # Overhang is the difference
    overhang = effective_length - d
    
    # Calculate offset angle
    # The offset angle is calculated using: β = arcsin((x₂ - x₁) / (2·L))
    # This is the angle between the cartridge centerline and the pivot-to-spindle line
    offset_angle = math.degrees(math.asin((outer_null - inner_null) / (2 * effective_length)))
    
    return inner_null, outer_null, effective_length, overhang, offset_angle

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
        # Use proper geometric solver
        effective_length, overhang, offset_angle = \
            calculate_effective_length_from_nulls(pivot_to_spindle, inner_null, outer_null)
        alignment_name = f"Custom ({inner_null:.2f}/{outer_null:.2f}mm)"
    else:
        inner_null, outer_null, effective_length, overhang, offset_angle = \
            calculate_null_points(pivot_to_spindle, alignment, inner_groove, outer_groove)
        alignment_name = ALIGNMENTS[alignment]['name']
    
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
    origin_y = height - 60*mm  # 60mm from top
    
    # Text column on right side (UNCHANGED - text stays in place)
    text_start_x = 125*mm  # Right column for all text
    
    # Title and specs at top right
    if custom_name:
        # Custom name: "Arc Protractor" on first line, name on second line
        c.setFont("Helvetica-Bold", 16)  # Increased from 14
        c.drawString(text_start_x, height - 40*mm, "Arc Protractor")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(text_start_x, height - 52*mm, custom_name)  # Adjusted position
        # Show alignment type smaller below
        c.setFont("Helvetica", 9)
        c.drawString(text_start_x, height - 60*mm, alignment_name)  # Adjusted position
    else:
        # Standard title
        c.setFont("Helvetica-Bold", 16)  # Increased from 14
        c.drawString(text_start_x, height - 40*mm, f"Arc Protractor")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(text_start_x, height - 52*mm, f"{alignment_name}")  # Adjusted
    
    # Specs with 6mm spacing between lines
    c.setFont("Helvetica", 9)
    c.drawString(text_start_x, height - 68*mm, f"Pivot to Spindle:")  # Adjusted from 66mm
    c.drawString(text_start_x + 40*mm, height - 68*mm, f"{pivot_to_spindle:.2f} mm")
    
    c.drawString(text_start_x, height - 74*mm, f"Effective Length:")
    c.drawString(text_start_x + 40*mm, height - 74*mm, f"{effective_length:.3f} mm")
    
    c.drawString(text_start_x, height - 80*mm, f"Overhang:")
    c.drawString(text_start_x + 40*mm, height - 80*mm, f"{overhang:.3f} mm")
    
    c.drawString(text_start_x, height - 86*mm, f"Inner Null:")
    c.drawString(text_start_x + 40*mm, height - 86*mm, f"{inner_null:.3f} mm")
    
    c.drawString(text_start_x, height - 92*mm, f"Outer Null:")
    c.drawString(text_start_x + 40*mm, height - 92*mm, f"{outer_null:.3f} mm")
    
    c.drawString(text_start_x, height - 98*mm, f"Offset Angle:")
    c.drawString(text_start_x + 40*mm, height - 98*mm, f"{offset_angle:.3f}°")
    
    # Instructions - SAME font size and spacing as specs
    c.setFont("Helvetica-Bold", 10)
    c.drawString(text_start_x, height - 110*mm, "INSTRUCTIONS:")  # Adjusted from 108mm
    
    c.setFont("Helvetica", 9)
    instructions = [
        "1. Print at 100% scale",
        "2. Verify 100mm bar below",
        "3. Cut out spindle hole",
        "4. Place on turntable",
        "5. Lower stylus onto arc",
        "6. At each null point:",
        "   - Stylus tip on black dot",
        "   - Cartridge parallel to grid lines",
        "7. Tighten when aligned"
    ]
    
    y_pos = height - 118*mm  # Adjusted from 116mm
    for line in instructions:
        c.drawString(text_start_x, y_pos, line)
        y_pos -= 6*mm
    
    # Scale verification at BOTTOM LEFT (below protractor area)
    scale_x = 20*mm  # Left side
    scale_y = 30*mm  # Near bottom
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(scale_x, scale_y + 20*mm, "SCALE VERIFICATION:")
    c.setFont("Helvetica", 9)
    c.drawString(scale_x, scale_y + 12*mm, "This bar must measure exactly:")
    
    # 100mm scale bar
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.6)
    c.line(scale_x, scale_y, scale_x + 100*mm, scale_y)
    c.line(scale_x, scale_y - 3*mm, scale_x, scale_y + 3*mm)
    c.line(scale_x + 100*mm, scale_y - 3*mm, scale_x + 100*mm, scale_y + 3*mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(scale_x + 37*mm, scale_y - 10*mm, "100.0 mm")
    
    # Footer at bottom left
    c.setFont("Helvetica", 6)
    c.drawString(scale_x, 15*mm, "arc_protractor_generator.py")
    c.drawString(scale_x, 10*mm, f"IEC Radii: {inner_groove:.1f}-{outer_groove:.1f}mm")
    
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
    
    # Spindle label - above spindle since it's now at top
    c.setFont("Helvetica-Bold", 9)
    c.drawString(6*mm, 6*mm, "SPINDLE")
    
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
        
        # Draw simple black dot for stylus position marker (BEFORE rotating)
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
    # Match spindle crosshair appearance
    c.setStrokeColorRGB(0, 0, 0)  # Black, same as spindle crosshairs
    c.setLineWidth(0.2)  # Same as spindle crosshairs
    
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
    draw_alignment_grid(inner_null, "Inner Null")
    draw_alignment_grid(outer_null, "Outer Null")
    
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
        
        # Draw stylus arc - match spindle crosshair appearance
        c.setStrokeColorRGB(0, 0, 0)  # Black, same as spindle crosshairs
        c.setLineWidth(0.2)  # Same as spindle crosshairs
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
        'offset_angle': offset_angle
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
        print(f"{'Alignment':<20} {'Inner Null':<12} {'Outer Null':<12} {'Eff. Length':<13} {'Overhang':<10} {'Offset°'}")
        print("-" * 85)
        
        for alignment_key in ['baerwald', 'lofgren_b', 'stevenson']:
            inner_null, outer_null, eff_len, overhang, offset = \
                calculate_null_points(args.pivot_to_spindle, alignment_key, 
                                     args.inner_groove, args.outer_groove)
            name = ALIGNMENTS[alignment_key]['name']
            print(f"{name:<20} {inner_null:>10.3f}mm {outer_null:>10.3f}mm {eff_len:>11.3f}mm {overhang:>8.3f}mm {offset:>7.3f}")
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
        print(f"  Offset Angle:      {specs['offset_angle']:.3f}°")
        print("\n⚠  IMPORTANT: Print at 100% scale and verify measurements!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
