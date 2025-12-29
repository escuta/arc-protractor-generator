# Arc Protractor Generator

Python script to generate precision arc protractors for aligning phono cartridges on turntables with pivoting tonearms.

## Features

- Three alignment geometries: Baerwald (Löfgren A), Löfgren B, and Stevenson
- Supports both A4 and US Letter paper sizes
- Geometrically accurate calculations using IEC standard groove radii
- Professional PDF output with verification scale bar
- Grid lines tilted to match null point geometry for precise alignment
- Extended grids to help align cartridge body along the tonearm axis

## Prerequisites

- Python 3.6 or later
- ReportLab library

## Installation
```bash
pip install reportlab
```

## Quick Start
```bash
# Generate protractor for your turntable
python3 arc_protractor_generator.py 215.7 --name "My Turntable"

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

# Show all alignment calculations
python3 arc_protractor_generator.py 215.5 --show-all
```

### Options

- `-a, --alignment`: Choose geometry (baerwald, lofgren_b, stevenson)
- `--papersize`: Paper size (A4, US, letter)
- `-o, --output`: Output PDF filename
- `--name`: Custom name for the protractor
- `--custom-nulls`: Custom null points in mm
- `--show-all`: Show calculations for all alignments

### Common Tonearm Distances

| Turntable/Tonearm | Pivot-to-Spindle Distance |
|-------------------|---------------------------|
| SME 3009 S2 Improved (early) | 215.5-215.7 mm |
| SME 3009 S2 Improved (late) | 213.25 mm |
| Technics SL-1200 | 215.0 mm |
| Rega RB300 | 222.0 mm |
| Pro-Ject 8.6" tonearms | 200.0 mm |

## How It Works

The script calculates the optimal null points (where tracking error = 0) based on your tonearm geometry and chosen alignment method. It generates a PDF with an arc matching your stylus path and alignment grids positioned at the null points.

## Alignment Geometries

### Baerwald (Löfgren A) - Default
- Minimizes maximum tracking error
- Best for general-purpose listening
- Null points: 66.04mm, 120.90mm

### Löfgren B
- Minimizes RMS (average) tracking error
- Best for full-side listening
- Null points: 70.29mm, 116.60mm

### Stevenson
- Minimizes tracking error at inner grooves
- Best for records with long inner groove sections
- Null points: 60.325mm, 146.05mm

## Printing Instructions

1. Print at 100% scale (NO scaling/fit-to-page)
2. Verify the 100mm scale bar measures exactly 100mm
3. Use the protractor to align your cartridge

## License

GPL (GNU General Public License)

## Credits

Iain Mott

## Related

- Blog post: [Your blog URL here]
- Detailed documentation: [Link if you have one]
