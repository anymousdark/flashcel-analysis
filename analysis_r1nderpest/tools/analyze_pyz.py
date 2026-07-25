"""
Analyze PYZ structure in detail
"""
import struct, os

OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\src'

with open(f'{OUT_DIR}/decompressed_all.bin', 'rb') as f:
    data = f.read()

# Show hex dump around PYZ position (offset 864)
print("=== Hex dump around PYZ (offset 840-920) ===")
for i in range(840, min(920, len(data)), 16):
    hex_str = ' '.join(f'{data[i+j]:02x}' for j in range(min(16, len(data)-i)))
    ascii_str = ''.join(chr(data[i+j]) if 32 <= data[i+j] <= 126 else '.' for j in range(min(16, len(data)-i)))
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

# PYZ magic = b'PYZ ' (with space) at offset 864
# After "PYZ " we have 4 bytes that we read as 1768708648
# Let me see what those bytes actually are
print(f"\nBytes at 864-872: {data[864:872].hex()} = {data[864:872]}")
print(f"As int32 little: {struct.unpack('<I', data[868:872])[0]}")

# After PYZ, in PyInstaller 6.x format:
# Actually the format may be different. Let me look at what comes before PYZ
# The CArchive TOC entries should be before the PYZ section

# Print decompressed data from start (offset 0 to 900)
print("\n=== Full decompressed data (0-900) ===")
for i in range(0, min(900, len(data)), 16):
    hex_str = ' '.join(f'{data[i+j]:02x}' for j in range(min(16, len(data)-i)))
    ascii_str = ''.join(chr(data[i+j]) if 32 <= data[i+j] <= 126 else '.' for j in range(min(16, len(data)-i)))
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

# The decompressed data starts with TOC entries from the CArchive
# TOC format: name + separator + type + data
# Types: 'm' = module, 's' = script, 'b' = binary, 'd' = dependency, 'z' = zlib archive

# Let me just extract all readable strings from the decompressed data
text = data.decode('latin-1')

# The first entries should be the TOC items
# Let me look for the pattern: module names followed by type codes
print("\n=== TOC entry analysis (around 0-200) ===")
section = text[:200]
print(section)

# Find specific patterns: the TOC entries have structure:
# type_byte + name + \x00 + data
# Types: m=module, s=script, b= binary, z= custom
print("\n=== TOC entries with type markers ===")
for i in range(min(500, len(data))):
    b = data[i]
    if b in (ord('m'), ord('s'), ord('b'), ord('z'), ord('d')):
        # Check if this starts a TOC entry
        name_end = data.find(b'\x00', i+1, i+200)
        if name_end > i+1:
            name = data[i+1:name_end].decode('latin-1', errors='replace')
            if len(name) > 3 and not any(c in name for c in '()[]{}'):
                # Show next 20 bytes after null
                next_bytes = data[name_end+1:name_end+21].hex()
                print(f"  type={chr(b)} name={name} next={next_bytes}")
