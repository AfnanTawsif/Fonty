# Fonty
A powerful **FontForge** Python script to replace (transfer) glyphs from one font to another based on Unicode codepoints or ranges specified by the user.

---

## ✨ Features
- 📝 Replace glyphs in a destination font with glyphs from a source font.
- 🔢 Specify one or both of:
  - A Unicode **range** (start & end hex codes).
  - A list of **specific Unicode hex values**.
- 🖋️ Choose **Y-alignment** mode:
  1. Keep source top.
  2. Match destination top.
  3. Match destination bottom.
- 📏 Copy bearings (advance width, left & right side bearings) from source glyph.
- 📝 Prompt for **new font name**, **author name**, and **license** text automatically.
- 📂 Automatic detection of fonts from “Source” and “Destination” folders.

---

## 📦 Requirements

### 1️⃣ FontForge
Fonty uses **FontForge’s Python API**, so you must run it using FontForge.

#### Debian/Ubuntu:
```bash
sudo apt update
sudo apt install fontforge python3-fontforge
```

#### Windows:
1. Download and install FontForge (Windows installer) from:  
   [https://fontforge.org/en-US/downloads/windows/](https://fontforge.org/en-US/downloads/windows/)
2. During installation, make sure **Python scripting** is enabled.
3. Add FontForge to your PATH (optional but recommended).

### 2️⃣ Python 
A system Python ≥3.6 is recommended if you edit or run scripts externally.  
However, the script itself runs inside FontForge’s own Python.

No extra pip libraries are required beyond what FontForge provides.

---

## 📂 Folder Structure

Before running, organize your folders like this:

```
Fonty.py
Source/        # Put your source font(s) here (.ttf or .otf)
Destination/   # Put your destination font(s) here (.ttf or .otf)
Output/        # Generated font(s) will appear here automatically
```

---

## 🚀 How to Run

From terminal (Linux/Mac):

```bash
fontforge -script Fonty.py
```

On Windows (cmd or PowerShell):

```powershell
"C:\Program Files (x86)\FontForgeBuilds\bin\fontforge.exe" -script Fonty.py
```

(Adjust the path to `fontforge.exe` if needed.)

---

## 📝 User Instructions

1. **Define Unicode Range**  
   (You can get the Unicode value for any glyph by opening a font using font forge > double clicking that glyph > Elements > Glyph info)
   - Enter *start* and *end* Unicode hex values (e.g., `0020` to `007F`).  
   - Leave blank if you don’t want a range.

3. **Define Specific Unicodes**  
   - Enter comma-separated Unicode hex values (e.g., `00A0, 00A9`).  
   - Leave blank if you don’t want specific ones.

4. **Enter Metadata**  
   - New Font Name (required).  
   - Author Name (required).  
   - License Text (optional, defaults to “© Author All rights reserved”).

5. **Select Source & Destination Fonts**  
   - Script automatically lists fonts found in the `Source` and `Destination` folders.  
   - If multiple are found, you’ll be prompted to pick one.

6. **Choose Y-Alignment Mode**  
   - `1` = Keep source top (default)- this option replicates the alignments of source glyphs. 
   - `2` = Match destination top.  
   - `3` = Match destination bottom.

7. **Processing**  
   - The script copies, scales, and aligns each glyph.  
   - Prints progress for each Unicode.

8. **Done**  
   - Modified font saved in `Output/` as `<NewFontName>.ttf`.

---

## 📝 Notes
- Always back up your fonts before running (just in case).
- FontForge sometimes logs warnings—these are usually harmless.
