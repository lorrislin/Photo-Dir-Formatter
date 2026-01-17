"""
Photo Folder Manager Script
===========================

DESCRIPTION:
This script organizes photo directories by:
1. Converting HEIC files to JPG and moving the original HEIC files to a 'heic/' subfolder.
2. Moving MOV files to a 'mov/' subfolder.
3. Moving MP4/MPG files to a 'mp4/' subfolder.

BEHAVIOR:
- Recursively scans the target directory provided by the user.
- Uses 'pillow-heif' for conversion logic.
- Handles file collisions (won't overwrite if the destination file already exists).
- Automatically creates subfolders ('heic', 'mov', 'mp4') inside each subfolder.
- VERIFICATION: Counts target files before processing and verifies counts in subfolders after.

PREREQUISITES:
    pip install Pillow pillow-heif

USAGE:
    python organize_photos.py <directory_path> [quality]
    Example: python organize_photos.py D:\heic_script_test 80
"""

import os
import shutil
import sys
from PIL import Image
from pillow_heif import register_heif_opener

# Initialize HEIF support
register_heif_opener()

def safe_move(src, dest_folder):
    """Moves a file to a destination folder safely, creating the folder if needed."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    filename = os.path.basename(src)
    dest_path = os.path.join(dest_folder, filename)
    
    if os.path.exists(dest_path):
        print(f"  [Skip Move] '{filename}' already exists in '{dest_folder}'.")
        return False
    
    try:
        shutil.move(src, dest_path)
        return True
    except Exception as e:
        print(f"  [Error] Could not move {filename}: {e}")
        return False

def count_files_in_folder(folder_path, extensions):
    """Counts files with specific extensions in a given folder."""
    if not os.path.exists(folder_path):
        return 0
    count = 0
    for file in os.listdir(folder_path):
        if file.lower().endswith(extensions):
            count += 1
    return count

def process_directory(current_path, quality=95):
    """Recursively crawls directories and organizes files."""
    # Normalizing path for the current OS
    current_path = os.path.normpath(current_path)
    
    if not os.path.isdir(current_path):
        return

    # Skip our own generated subfolders
    folder_name = os.path.basename(current_path).lower()
    if folder_name in ['heic', 'mov', 'mp4']:
        return

    print(f"\nScanning: {current_path}")

    try:
        # Get all items in the current directory
        with os.scandir(current_path) as it:
            entries = list(it)
            
        # First, recurse into subdirectories
        for entry in entries:
            if entry.is_dir():
                process_directory(entry.path, quality)

        # Before processing files in CURRENT directory, perform count
        target_counts = {
            'heic': 0,
            'mov': 0,
            'mp4': 0
        }
        
        heic_exts = ('.heic', '.heif')
        mov_exts = ('.mov',)
        mp4_exts = ('.mp4', '.mpg', '.mpeg')

        files_to_process = []
        for entry in entries:
            if entry.is_file():
                file_lower = entry.name.lower()
                if file_lower.endswith(heic_exts):
                    target_counts['heic'] += 1
                    files_to_process.append(entry)
                elif file_lower.endswith(mov_exts):
                    target_counts['mov'] += 1
                    files_to_process.append(entry)
                elif file_lower.endswith(mp4_exts):
                    target_counts['mp4'] += 1
                    files_to_process.append(entry)

        # Only proceed if there are files to organize in this folder
        total_targets = sum(target_counts.values())
        if total_targets == 0:
            return

        print(f"  [Info] Found {total_targets} target files (HEIC: {target_counts['heic']}, MOV: {target_counts['mov']}, MP4/MPG: {target_counts['mp4']})")

        # Then, process files in the current directory
        for entry in files_to_process:
            file_path = entry.path
            file_lower = entry.name.lower()
            base_name = os.path.splitext(entry.name)[0]

            # 1. Handle HEIC Files
            if file_lower.endswith(heic_exts):
                jpg_path = os.path.join(current_path, f"{base_name}.jpg")
                
                if not os.path.exists(jpg_path):
                    try:
                        print(f"  [Convert] {entry.name} -> {base_name}.jpg")
                        img = Image.open(file_path)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        img.save(jpg_path, "JPEG", quality=quality)
                    except Exception as e:
                        print(f"  [Error] Failed to convert {entry.name}: {e}")
                        continue
                else:
                    print(f"  [Skip Conv] {base_name}.jpg already exists.")

                heic_folder = os.path.join(current_path, "heic")
                if safe_move(file_path, heic_folder):
                    print(f"  [Moved] {entry.name} to heic/")

            # 2. Handle MOV Files
            elif file_lower.endswith(mov_exts):
                mov_folder = os.path.join(current_path, "mov")
                if safe_move(file_path, mov_folder):
                    print(f"  [Moved] {entry.name} to mov/")

            # 3. Handle MP4 / MPG Files
            elif file_lower.endswith(mp4_exts):
                mp4_folder = os.path.join(current_path, "mp4")
                if safe_move(file_path, mp4_folder):
                    print(f"  [Moved] {entry.name} to mp4/")

        # VERIFICATION STEP
        print(f"  [Verify] Checking folder integrity...")
        actual_heic = count_files_in_folder(os.path.join(current_path, "heic"), heic_exts)
        actual_mov = count_files_in_folder(os.path.join(current_path, "mov"), mov_exts)
        actual_mp4 = count_files_in_folder(os.path.join(current_path, "mp4"), mp4_exts)

        is_correct = (actual_heic == target_counts['heic'] and 
                      actual_mov == target_counts['mov'] and 
                      actual_mp4 == target_counts['mp4'])

        if is_correct:
            print(f"  [Result] Success: All {total_targets} files accounted for in subfolders.")
        else:
            print(f"  [Result] WARNING: Count mismatch!")
            print(f"    - HEIC: expected {target_counts['heic']}, found {actual_heic}")
            print(f"    - MOV:  expected {target_counts['mov']}, found {actual_mov}")
            print(f"    - MP4:  expected {target_counts['mp4']}, found {actual_mp4}")

    except PermissionError:
        print(f"  [Error] Permission denied: {current_path}")
    except Exception as e:
        print(f"  [Error] Unexpected error in {current_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing mandatory directory path.")
        print("Usage: python organize_photos.py <directory_path> [quality]")
        sys.exit(1)
        
    start_dir = sys.argv[1]
    jpg_quality = 95
    
    if len(sys.argv) > 2:
        try:
            val = int(sys.argv[2])
            if 1 <= val <= 100:
                jpg_quality = val
            else:
                print(f"Quality {val} out of range (1-100). Using default 95.")
        except ValueError:
            print("Invalid quality argument. Using default 95.")
    
    if not os.path.exists(start_dir):
        print(f"Error: Path '{start_dir}' does not exist.")
        sys.exit(1)

    print(f"Starting organization in: {os.path.abspath(start_dir)}")
    print(f"Target Quality: {jpg_quality}")
    print("-" * 50)
    
    process_directory(start_dir, quality=jpg_quality)
    
    print("\n" + "-" * 50)
    print("Organization complete!")