"""
HEIC to JPG Converter Script
============================

DESCRIPTION:
This script converts high-efficiency image files (.heic, .heif) created by Apple devices
into standard JPEG files (.jpg). 

BEHAVIOR:
1. Validates the existence of the input file.
2. Checks that the input file has a .heic or .heif extension.
3. Automatically names the output file by replacing the extension with .jpg.
4. SAFETY: Checks if a .jpg with the same name already exists. If so, it shows a 
   warning and skips the conversion to prevent overwriting your data.
5. Handles alpha channels (transparency) by converting the image to RGB mode.
6. Allows for custom JPEG compression quality (default is 95).

PREREQUISITE PACKAGES:
This script requires the following Python libraries:
- Pillow (PIL): The standard Python Imaging Library.
- pillow-heif: An extension for Pillow to support HEIF/HEIC formats.

INSTALLATION GUIDE:
Open your terminal or command prompt and run:
    pip install Pillow pillow-heif

EXAMPLE USAGE:
    Default (Quality 95):  python convert.py img1.heic
    Custom Quality:        python convert.py img1.heic 80
"""

import os
import sys
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF opener with Pillow to enable .open() for HEIC files
register_heif_opener()

def convert_heic_to_jpg(input_path, quality=95):
    """
    Converts a HEIC image to JPG with specified compression quality.
    """
    # 1. Check if the file exists
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    # 2. Check if the file is a HEIC file
    if not input_path.lower().endswith(('.heic', '.heif')):
        print(f"Error: '{input_path}' is not a HEIC/HEIF file.")
        return

    # 3. Create the output path (replace extension with .jpg)
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}.jpg"

    # 4. Check if output file already exists (Safety Check)
    if os.path.exists(output_path):
        print(f"Warning: '{output_path}' already exists. Skipping conversion to prevent overwrite.")
        return

    try:
        # 5. Perform the conversion
        print(f"Converting '{input_path}' to '{output_path}' (Quality: {quality})...")
        image = Image.open(input_path)
        
        # Convert to RGB if necessary (HEIC can be CMYK or have Alpha, JPG must be RGB)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        image.save(output_path, "JPEG", quality=quality)
        print("Conversion successful!")
        
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    # Check if at least a filename was provided
    if len(sys.argv) < 2:
        print("Usage: python convert.py <filename.heic> [quality]")
        print("Example: python convert.py image.heic 80")
    else:
        file_to_convert = sys.argv[1]
        
        # Set default quality or use provided argument
        jpg_quality = 95
        if len(sys.argv) >= 3:
            try:
                jpg_quality = int(sys.argv[2])
                # Ensure quality is within valid bounds for JPEG (1-100)
                if not (1 <= jpg_quality <= 100):
                    print("Quality must be between 1 and 100. Using default of 95.")
                    jpg_quality = 95
            except ValueError:
                print("Invalid quality value provided. Using default of 95.")
                
        convert_heic_to_jpg(file_to_convert, quality=jpg_quality)