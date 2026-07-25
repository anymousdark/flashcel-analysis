"""
Extract and disassemble all Python code objects from R1nderPest
"""
import sys, os, marshal, dis

sys.path.insert(0, r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\tools')
from extract_tools import find_overlay, decompress_streams, extract_all_marshal, save_disassembly

EXE_PATH = r'C:\R1nderpest\r1nderpest.exe'
OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\src'
DESKTOP_DIR = r'C:\Users\Aycher\Desktop\R1nderPest_Cracked\src'

# Extract and decompress
print("Step 1: Finding overlay...")
data, overlay_start, overlay = find_overlay(EXE_PATH)
print(f"  Overlay: {len(overlay)} bytes at 0x{overlay_start:x}")

print("Step 2: Decompressing zlib streams...")
decompressed = decompress_streams(overlay, max_streams=2000)
print(f"  Decompressed: {len(decompressed)} bytes")

print("Step 3: Extracting marshal code objects...")
codes = extract_all_marshal(decompressed)
print(f"  Found {len(codes)} code objects")

# Save all disassemblies
disasm_path = os.path.join(OUT_DIR, 'full_disassembly.txt')
with open(disasm_path, 'w', encoding='utf-8') as f:
    f.write(f"# R1nderPest v2.4 - Full Python Bytecode Disassembly\n")
    f.write(f"# Total code objects: {len(codes)}\n\n")
    
    for pos, size, code_obj in codes:
        f.write(f"\n{'#'*60}\n")
        f.write(f"# Code object at offset {pos}, size {size}\n")
        f.write(f"# File: {code_obj.co_filename}\n")
        f.write(f"# Name: {code_obj.co_name}\n")
        f.write(f"# First line: {code_obj.co_firstlineno}\n")
        f.write(f"# Args: {code_obj.co_argcount}, Stack: {code_obj.co_stacksize}\n")
        f.write(f"{'#'*60}\n")
        dis.dis(code_obj, file=f)
        f.write("\n")

print(f"Saved: full_disassembly.txt")

# Also extract new_r1nderpest specifically
for pos, size, code_obj in codes:
    if 'new_r1nderpest' in code_obj.co_filename:
        out = os.path.join(OUT_DIR, 'new_r1nderpest_disasm.txt')
        save_disassembly(code_obj, out)
        print(f"Saved: new_r1nderpest_disasm.txt")
        break

# Save constants and strings from all code objects
strings_path = os.path.join(OUT_DIR, 'python_constants.txt')
all_strings = set()
all_consts = set()
for pos, size, code_obj in codes:
    for const in code_obj.co_consts:
        if isinstance(const, str):
            all_strings.add(const)
        elif isinstance(const, (int, float)):
            all_consts.add(str(const))
        elif hasattr(const, 'co_code'):
            all_consts.add(f"<code: {const.co_name} @ {const.co_filename}>")

with open(strings_path, 'w', encoding='utf-8') as f:
    f.write("=== String Constants ===\n")
    for s in sorted(all_strings):
        if len(s) > 2 and any(c.isalpha() for c in s):
            f.write(s + "\n")
    f.write(f"\nTotal strings: {len(all_strings)}\n")
print(f"Saved: python_constants.txt ({len(all_strings)} strings)")

# Copy to desktop
import shutil
for fname in ['full_disassembly.txt', 'new_r1nderpest_disasm.txt', 'python_constants.txt']:
    src = os.path.join(OUT_DIR, fname)
    dst = os.path.join(DESKTOP_DIR, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)

print("\nDone!")
