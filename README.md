# Arc Protractor Generator

Python script to generate precision arc protractors for aligning phono cartridges on turntables with pivoting tonearms.

## Features

- Three alignment geometries: Baerwald (Löfgren A), Löfgren B, and Stevenson
- Custom null point support for experimental or specialized alignments
- Support for custom groove radii (45 RPM singles, 78 RPM records, etc.)
- Bilingual support: English and Portuguese
- Supports both A4 and US Letter paper sizes
- Geometrically accurate calculations using IEC standard groove radii
- PDF output with verification scale bar
- Optional custom naming for different tonearms/turntables

## Web Interface

Try the online generator at: [https://escuta.org/en/outro/arc-protractor-generator.html](https://escuta.org/en/outro/arc-protractor-generator.html)

Available in:
- English: [https://escuta.org/en/outro/arc-protractor-generator.html](https://escuta.org/en/outro/arc-protractor-generator.html)
- Portuguese: [https://escuta.org/pt/outro/arc-protractor-generator.html](https://escuta.org/pt/outro/arc-protractor-generator.html)

## Prerequisites

- Python 3.6 or later
- ReportLab library

## Installation

### Using pip
```bash
pip install reportlab
```

### On Arch Linux
```bash
sudo pacman -S python-reportlab
```

## Quick Start
```bash
# Generate protractor for your turntable
python3 arc_protractor_generator.py 215.7 --name "My Turntable"

# Generate Portuguese version
python3 arc_protractor_generator.py 215.7 --name "Meu Toca-discos" --language pt

# Print the PDF at 100% scale and verify the 100mm scale bar
```

## Usage
```bash
python3 arc_protractor_generator.py <pivot_to_spindle_distance> [options]
```

### Common Examples
```bash
# SME 3009 S2 Improved with Baerwald alignment
python3 arc_protractor_generator.py 215.5

# Pro-Ject turntable with US Letter paper
python3 arc_protractor_generator.py 200.0 --papersize US

# Technics SL-1200 with Löfgren B alignment
python3 arc_protractor_generator.py 215.0 --alignment lofgren_b

# Portuguese language protractor
python3 arc_protractor_generator.py 215.5 --language pt

# Custom null points (experimental alignment)
python3 arc_protractor_generator.py 215.5 --custom-nulls 66.0 120.9

# 7" 45 RPM single with custom groove radii
python3 arc_protractor_generator.py 215.5 --inner-groove 57.5 --outer-groove 89.0

# Show all alignment calculations
python3 arc_protractor_generator.py 215.5 --show-all
```

### Options

- `-a, --alignment`: Choose geometry (baerwald, lofgren_b, stevenson)
- `--papersize`: Paper size (A4, US, letter)
- `--language`: Language for labels (en, pt)
- `-o, --output`: Output PDF filename
- `--name`: Custom name for the protractor
- `--custom-nulls INNER OUTER`: Custom null points in mm (overrides alignment type)
- `--inner-groove`: Inner groove radius in mm (default: 60.325 IEC)
- `--outer-groove`: Outer groove radius in mm (default: 146.05 IEC)
- `--show-all`: Show calculations for all alignments

### Common Tonearm Distances

**9" tonearms:**
- SME 3009 S2 Improved (early): 215.7 mm
- SME 3009 S2 Improved (late): 213.25 mm
- Technics SL-1200: 215.0 mm
- Rega RB300: 222.0 mm
- Audio-Technica AT-LP120: 215.0 mm
- Pro-Ject 8.6" tonearms: 200.0 mm

**12" tonearms:**
- SME M2-12R: 295.6 mm

## How It Works

The script calculates the optimal null points (where tracking error = 0) based on your tonearm geometry and chosen alignment method. It generates a PDF with an arc matching your stylus path and alignment grids precisely positioned at the null points. The protractor allows you to set both the overhang (the distance the stylus extends beyond the spindle) and offset angle (cartridge rotation) simultaneously by aligning the stylus with the arc and grid lines at both null points.

## Alignment Geometries

### Baerwald (Löfgren A) - Default
- Minimizes maximum tracking error
- Best for general-purpose listening
- Null points: 66.04mm, 120.90mm (for IEC standard grooves)

### Löfgren B
- Minimizes RMS (average) tracking error
- Best for full-side listening
- Null points: 70.29mm, 116.60mm (for IEC standard grooves)

### Stevenson
- Minimizes tracking error at inner grooves
- Best for records with long inner groove sections
- Null points: 60.325mm, 117.42mm (for IEC standard grooves)

## Alignment for Other Record Formats

The script provides preset groove standards and allows custom values for specialized formats.

### Standard Groove Specifications

**IEC/RIAA (60.325-146.05mm)** - International standard used for most modern 12" LPs manufactured worldwide.

**DIN (57.5-146.05mm)** - German standard with smaller inner groove radius, historically used by some European manufacturers.

### About Custom Groove Radii

The script provides preset groove standards for convenience. For these standard values, the protractor uses precisely optimized null points derived from published alignment standards.

When you enter custom groove dimensions (different from any preset), the generator approximates optimal null points by scaling from the nearest standard. This scaling preserves the distortion balance characteristics of each alignment geometry—the mathematical relationship between null point placement and tracking error distribution.

### Common Custom Format Examples

**7" 45 RPM Singles**
- Typical groove radii: 57-58mm (inner) to 88-90mm (outer)
- Example: `python3 arc_protractor_generator.py 215.5 --inner-groove 57.5 --outer-groove 89.0`

**10" 78 RPM Records**
- Typical groove radii: 60-62mm (inner) to 117-120mm (outer)
- For single-track recordings, Löfgren B alignment is recommended
- Example: `python3 arc_protractor_generator.py 215.5 --alignment lofgren_b --inner-groove 61.0 --outer-groove 118.0`

**12" 78 RPM Records**
- Typical groove radii: 60-65mm (inner) to 135-145mm (outer)
- Example: `python3 arc_protractor_generator.py 215.5 --inner-groove 62.0 --outer-groove 140.0`

*Note: 78 RPM records pre-date standardization and groove radii varied by manufacturer and era. The values above are typical approximations.*

## How to Use the Protractor

1. **Place the Protractor:** Centre the protractor on your turntable spindle, ensuring it's the correct one for your tonearm's pivot-to-spindle distance.

2. **Loosen Cartridge:** Slightly loosen the cartridge mounting screws so the cartridge can slide forward and backward in the headshell.

3. **Align at Outer Null Point:**
   - Lower the stylus onto the outer alignment grid
   - Adjust the cartridge's forward/backward position (overhang) so the stylus tip sits precisely on the arc
   - Simultaneously adjust the cartridge's angle so its body or cantilever is parallel to the grid lines

4. **Check Inner Null Point:**
   - Move the tonearm to the inner alignment grid without moving the protractor
   - If the stylus doesn't align perfectly with the arc and grid, adjust the cartridge position again

5. **Iterate:** Return to the outer point and recheck alignment, then back to the inner point, repeating until the stylus tracks the arc and aligns with both grids perfectly.

6. **Tighten:** Once aligned at both points, carefully tighten the mounting screws without shifting the cartridge position.

## Printing Instructions

1. Print the PDF at **100% scale** (NO scaling/fit-to-page)
2. Verify the 100mm scale bar measures exactly 100mm with a ruler
3. Use the protractor to align your cartridge following the steps above

**Note:** Some printers may have slight vertical axis compression (typically ~0.4%). Testing on a laser printer may improve accuracy. The protractor will work excellently for cartridge alignment even with minor printer variations.

## Web Form Installation

The repository includes a complete web form interface (`generate-protractor.php`, `protractor-form.js`, and HTML form files) that can be integrated into any website. The PHP script calls the Python generator and returns the PDF directly to the user's browser.

### Requirements
- PHP 7.4 or later
- Python 3.6+ with ReportLab installed
- Web server (Apache, Nginx, etc.)

### Installation
1. Place `arc_protractor_generator.py` and `generate-protractor.php` in the same directory (e.g., `/protractor/`)
2. Place `protractor-form.js` in your site's JavaScript directory
3. Integrate the form HTML into your pages (separate files provided for English and Portuguese)
4. Ensure the PHP script has permission to execute Python and write to the temp directory

## Language Support

The generator supports both English and Portuguese output. Use the `--language` flag:

```bash
# English (default)
python3 arc_protractor_generator.py 215.5 --language en

# Portuguese
python3 arc_protractor_generator.py 215.5 --language pt
```

## License

GPL (GNU General Public License)

## Credits

Created by Iain Mott
- Website: [https://escuta.org](https://escuta.org)
- GitHub: [https://github.com/escuta/arc-protractor-generator](https://github.com/escuta/arc-protractor-generator)

## Contributing

Contributions are welcome. Feel free to submit a Pull Request.
