"""
Extract PYZ archive from R1nderPest decompressed data and decompile Python code
"""
import zlib, struct, marshal, dis, os, sys

EXE_PATH = r'C:\R1nderpest\r1nderpest.exe'
OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\src'
DESKTOP_DIR = r'C:\Users\Aycher\Desktop\R1nderPest_Cracked\src'

with open(EXE_PATH, 'rb') as f:
    data = f.read()

# Find overlay start (last section end)
pe_off = struct.unpack('<I', data[0x3C:0x40])[0]
opt_hdr_sz = struct.unpack('<H', data[pe_off+20:pe_off+22])[0]
sec_start = pe_off + 24 + opt_hdr_sz
sections = struct.unpack('<H', data[pe_off+6:pe_off+8])[0]
last_end = 0
for i in range(sections):
    s = sec_start + i * 40
    raw_sz = struct.unpack('<I', data[s+16:s+20])[0]
    raw_ptr = struct.unpack('<I', data[s+20:s+24])[0]
    end = raw_ptr + raw_sz
    if end > last_end: last_end = end

overlay = data[last_end:]

# Decompress enough streams to get the PYZ
streams = []
pos = 0
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

all_decompressed = bytearray()
for i in range(min(2000, len(streams)-1)):
    start = streams[i]
    end = streams[i+1] if i+1 < len(streams) else start + 200000
    chunk = overlay[start:end]
    try:
        dec = zlib.decompressobj()
        out = dec.decompress(chunk)
        all_decompressed.extend(out)
    except:
        pass

# Find PYZ in decompressed data
pyz_pos = all_decompressed.find(b'PYZ')
if pyz_pos < 0:
    print("PYZ not found!")
    sys.exit(1)

print(f"PYZ at offset {pyz_pos} in decompressed data")

# PyInstaller PYZ format:
# struct PYZ {
#   char magic[4];  // "PYZ\0"
#   int toc_len;
#   unsigned char data[];  // zlib compressed TOC
# }

pyz_magic = all_decompressed[pyz_pos:pyz_pos+4]
print(f"PYZ magic: {pyz_magic}")

# Actually, PyInstaller's PYZ is stored differently.
# The PYZ is a struct: magic(4) + unused(4) + compressed_data
# The compressed_data when decompressed yields the TOC and the module data

# Let me look at the structure more carefully
# After PYZ\0, there should be a 32-bit length, then zlib-compressed TOC
toc_comp_len = struct.unpack('<I', all_decompressed[pyz_pos+4:pyz_pos+8])[0]
print(f"TOC compressed length from header: {toc_comp_len}")

# Actually wait, for PyInstaller 6.x the format is different
# Let me look at what's after PYZ
print(f"Bytes after PYZ: {all_decompressed[pyz_pos+4:pyz_pos+20].hex()}")

# Try different format: PYZ + zlib stream directly
# The data after PYZ\0 might be:
# 4 bytes: uncompressed size
# then zlib compressed data

toc_uncomp_len = struct.unpack('<I', all_decompressed[pyz_pos+4:pyz_pos+8])[0]
print(f"Next 4 bytes as int: {toc_uncomp_len}")

# Try to zlib decompress starting from pyz_pos+8
try:
    compressed_data = bytes(all_decompressed[pyz_pos+8:pyz_pos+8+200000])
    decomp_toc = zlib.decompress(compressed_data)
    print(f"TOC decompressed: {len(decomp_toc)} bytes")
    print(f"First 200 bytes: {decomp_toc[:200]}")
    
    # Save TOC
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f'{OUT_DIR}/pyz_toc.bin', 'wb') as f:
        f.write(decomp_toc)
    print("Saved: pyz_toc.bin")
except Exception as e:
    print(f"TOC decompress failed: {e}")
    
    # Try offset pyz_pos+4 directly as zlib
    try:
        compressed_data = bytes(all_decompressed[pyz_pos+4:pyz_pos+4+200000])
        decomp_toc = zlib.decompress(compressed_data)
        print(f"TOC decompressed (direct): {len(decomp_toc)} bytes")
        with open(f'{OUT_DIR}/pyz_toc.bin', 'wb') as f:
            f.write(decomp_toc)
    except Exception as e2:
        print(f"Direct decompress also failed: {e2}")

# Also save all decompressed data for reference
with open(f'{OUT_DIR}/decompressed_all.bin', 'wb') as f:
    f.write(all_decompressed)
print(f"Saved: decompressed_all.bin ({len(all_decompressed)} bytes)")

# Try to extract the main module 'new_r1nderpest' from decompressed data
# In the PYZ format, module data follows the TOC
# Each entry in TOC: len(4) + len_data(4) + name + compressed_data

# Actually, let me try to find marshal code objects in the decompressed data
# Python code objects start with byte 0x63 ('c') followed by a marshalled struct
# Let me look for Python code object signatures

text = bytes(all_decompressed).decode('latin-1')

# Find references to new_r1nderpest in decompressed context
idx = text.find('new_r1nderpest')
if idx >= 0:
    print(f"\n=== new_r1nderpest context ===")
    # Print surrounding area (2KB before and after)
    start = max(0, idx - 1000)
    end = min(len(text), idx + 3000)
    section = text[start:end]
    clean = ''.join(c if 32 <= ord(c) <= 126 else '\n' for c in section)
    with open(f'{OUT_DIR}/new_r1nderpest_context.txt', 'w', encoding='utf-8') as f:
        f.write(clean)
    print(f"Saved: new_r1nderpest_context.txt")

# Extract Python file-like references
import re
py_files = set()
for m in re.finditer(r'[a-zA-Z_][\w/]+\.py', text):
    path = m.group()
    if len(path) > 5 and 'typeshed' not in path and 'third_party' not in path:
        py_files.add(path)

print(f"\n=== Python files referenced ===")
with open(f'{OUT_DIR}/python_file_refs.txt', 'w', encoding='utf-8') as f:
    for pf in sorted(py_files):
        f.write(pf + '\n')
        print(f"  {pf}")

# Copy to desktop
import shutil
for folder in ['report', 'src']:
    src = f'C:\\Users\\Aycher\\Documents\\Default Project\\analysis_r1nderpest\\{folder}'
    dst = f'C:\\Users\\Aycher\\Desktop\\R1nderPest_Cracked\\{folder}'
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
            print(f"Copied: {item}")

print("\nDone!")
