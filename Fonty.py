#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fonty: Font Glyph Replacer
--------------------------

A FontForge Python script to replace glyphs in a destination font with
glyphs from a source font based on user-defined Unicode codepoints.

Features:
- Choose y-alignment method (1 = source top, 2 = destination top, 3 = destination bottom).
- Copy bearings (advance width, lsb, rsb) from source font.
- Mandatory font name and author name.
- Default license if left blank.
"""

import os
import shutil
import sys
import traceback

try:
    import fontforge
    import psMat
except ImportError:
    print("ERROR: FontForge modules not found.")
    print("Run with FontForge: fontforge -script Fonty.py")
    sys.exit(1)

# --- Helpers ---

def parse_hex_int(s):
    try:
        s_clean = s.strip().lower()
        if s_clean.startswith("0x"):
            s_clean = s_clean[2:]
        if not s_clean:
            return None
        val = int(s_clean, 16)
        if 0 <= val <= 0x10FFFF:
            return val
    except Exception:
        pass
    return None

def find_font_files(folder):
    if not os.path.isdir(folder):
        return []
    return [f for f in os.listdir(folder) if f.lower().endswith((".ttf", ".otf"))]

def choose_file(folder, role):
    files = find_font_files(folder)
    if not files:
        print(f"Error: No fonts found in {folder}")
        return None
    if len(files) == 1:
        print(f"Found {role} font: {files[0]}")
        return os.path.join(folder, files[0])
    print(f"Multiple fonts found for {role}:")
    for i, f in enumerate(files):
        print(f"  [{i}] {f}")
    choice = input(f"Choose {role} font number (default 0): ").strip()
    try:
        idx = int(choice) if choice else 0
        return os.path.join(folder, files[idx])
    except Exception:
        return os.path.join(folder, files[0])

# --- Main ---

def main():
    print("=== Fonty: Font Glyph Replacer ===")

    source_folder = "Source"
    dest_folder = "Destination"
    output_folder = "Output"
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Collect codepoints
    codepoints = set()
    print("\n--- Step 1: Define Unicode Range ---")
    start_s = input("Start Unicode (hex): ").strip()
    end_s = input("End Unicode (hex): ").strip()
    if start_s and end_s:
        start_cp = parse_hex_int(start_s)
        end_cp = parse_hex_int(end_s)
        if start_cp is not None and end_cp is not None and end_cp >= start_cp:
            for cp in range(start_cp, end_cp + 1):
                codepoints.add(cp)
            print(f"✅ Added range U+{start_cp:04X}–U+{end_cp:04X}")

    print("\n--- Step 2: Define Specific Unicodes ---")
    specific_s = input("Specific Unicodes (comma hex): ").strip()
    if specific_s:
        for part in specific_s.split(","):
            cp = parse_hex_int(part)
            if cp is not None:
                codepoints.add(cp)
                print(f"✅ Added U+{cp:04X}")

    if not codepoints:
        print("No codepoints provided. Exiting.")
        sys.exit(0)

    final_codepoints = sorted(codepoints)

    # Step 3: Metadata
    print("\n--- Step 3: Metadata ---")
    while True:
        new_font_name = input("Enter new font name: ").strip()
        if new_font_name:
            break
        print("❌ Font name cannot be empty.")
    while True:
        author_name = input("Enter author name: ").strip()
        if author_name:
            break
        print("❌ Author name cannot be empty.")

    license_text = input("Enter license text (optional): ").strip()
    if not license_text:
        license_text = f"© {author_name} All rights reserved"

    # Step 4: Font selection
    source_path = choose_file(source_folder, "Source")
    dest_path = choose_file(dest_folder, "Destination")
    if not source_path or not dest_path:
        sys.exit(1)

    # Dynamically keep the same extension as the destination font
    ext = os.path.splitext(dest_path)[1].lower()  # e.g. ".ttf" or ".otf"
    if ext not in [".ttf", ".otf"]:
        ext = ".ttf"  # fallback just in case

    output_path = os.path.join(output_folder, f"{new_font_name}{ext}")
    shutil.copy2(dest_path, output_path)


    # Step 5: Open fonts
    try:
        src_font = fontforge.open(source_path)
        out_font = fontforge.open(output_path)
    except Exception as e:
        print(f"Error opening fonts: {e}")
        sys.exit(1)

    # Metadata
    out_font.fontname = new_font_name.replace(" ", "")
    out_font.familyname = new_font_name
    out_font.fullname = new_font_name
    out_font.appendSFNTName('English (US)', 'Designer', author_name)
    out_font.copyright = f"Copyright 2025: {author_name}"
    out_font.appendSFNTName('English (US)', 'License', license_text)

    # Scale factor
    scale_factor = out_font.em / src_font.em
    print(f"\nScale factor = {scale_factor:.3f}")

    # Step 6: Alignment choice
    print("\n--- Step 6: Y-Alignment ---")
    print("1 = keep source top")
    print("2 = match destination top")
    print("3 = match destination bottom")
    choice = input("Choose (default 1): ").strip()
    align_mode = choice if choice in {"1","2","3"} else "1"
    print(f"Y-alignment mode = {align_mode}")

    replaced, skipped = 0, 0

    for cp in final_codepoints:
        try:
            if cp not in src_font or not src_font[cp].isWorthOutputting():
                print(f"U+{cp:04X} missing in source. Skipped.")
                skipped += 1
                continue

            old_top_y, old_bot_y = None, None
            if cp in out_font and out_font[cp].isWorthOutputting():
                box = out_font[cp].boundingBox()
                old_bot_y, old_top_y = box[1], box[3]

            # Clear and paste glyph
            out_font.selection.none()
            out_font.selection.select(cp)
            out_font.clear()
            src_font.selection.none()
            src_font.selection.select(cp)
            src_font.copy()
            out_font.selection.select(cp)
            out_font.paste()

            g = out_font[cp]
            g.transform(psMat.scale(scale_factor))

            # Y-alignment
            new_box = g.boundingBox()
            new_bot_y, new_top_y = new_box[1], new_box[3]
            shift_y = 0
            if align_mode == "2" and old_top_y is not None:
                shift_y = old_top_y - new_top_y
            elif align_mode == "3" and old_bot_y is not None:
                shift_y = old_bot_y - new_bot_y
            g.transform(psMat.translate(0, shift_y))

            # X-bearings (copy from source glyph, scale, and cast to int)
            g.width = int(round(src_font[cp].width * scale_factor))
            g.left_side_bearing = int(round(src_font[cp].left_side_bearing * scale_factor))
            g.right_side_bearing = int(round(src_font[cp].right_side_bearing * scale_factor))

            print(f"✓ U+{cp:04X} replaced.")
            replaced += 1

        except Exception as e:
            print(f"✗ U+{cp:04X} error: {e}")
            print(traceback.format_exc())

    # Save
    out_font.generate(output_path)
    print("\n✅ Done.")
    print(f"Replaced {replaced}, skipped {skipped}.")
    print(f"Output saved: {output_path}")

    src_font.close()
    out_font.close()

if __name__ == "__main__":
    main()
