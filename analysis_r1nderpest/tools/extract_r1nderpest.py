"""
Extract and analyze R1nderPest PyInstaller archive
"""
import zlib, struct, re, os, sys, marshal, dis, types

EXE_PATH = r'C:\R1nderpest\r1nderpest.exe'
OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest'

with open(EXE_PATH, 'rb') as f:
    data = f.read()

# === Step 1: PE header info (no rz-bin) ===
pe_info = []
pe_info.append("=== File Info ===")
pe_info.append(f"Size: {len(data)} bytes ({len(data)/1024/1024:.1f} MB)")
pe_info.append(f"MZ: {data[:2] == b'MZ'}")

pe_off = struct.unpack('<I', data[0x3C:0x40])[0]
pe_info.append(f"PE offset: 0x{pe_off:x}")
machine = struct.unpack('<H', data[pe_off+4:pe_off+6])[0]
machines = {0x14c:'I386', 0x8664:'AMD64', 0xaa64:'ARM64'}
pe_info.append(f"Machine: {machines.get(machine, f'0x{machine:x}')}")
sections = struct.unpack('<H', data[pe_off+6:pe_off+8])[0]
pe_info.append(f"Sections: {sections}")
ts = struct.unpack('<I', data[pe_off+8:pe_off+12])[0]
import datetime
pe_info.append(f"Timestamp: {datetime.datetime.fromtimestamp(ts)}")

# Section info
opt_hdr_sz = struct.unpack('<H', data[pe_off+20:pe_off+22])[0]
sec_start = pe_off + 24 + opt_hdr_sz
pe_info.append(f"\n=== Sections ===")
last_end = 0
for i in range(sections):
    s = sec_start + i * 40
    name = data[s:s+8].rstrip(b'\x00').decode('ascii', errors='replace')
    vsize = struct.unpack('<I', data[s+8:s+12])[0]
    vaddr = struct.unpack('<I', data[s+12:s+16])[0]
    raw_sz = struct.unpack('<I', data[s+16:s+20])[0]
    raw_ptr = struct.unpack('<I', data[s+20:s+24])[0]
    end = raw_ptr + raw_sz
    pe_info.append(f"  {name}: raw=0x{raw_ptr:x} size={raw_sz} end=0x{end:x} vsize={vsize}")
    if end > last_end: last_end = end

overlay_sz = len(data) - last_end
pe_info.append(f"\nOverlay: {overlay_sz} bytes ({overlay_sz/1024/1024:.1f} MB)")
pe_info.append(f"Sections: {last_end} bytes ({last_end/1024:.1f} KB)")

with open(f'{OUT_DIR}/report/file_info.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(pe_info))
print("Saved: file_info.txt")

# === Step 2: Extract strings from PE sections ===
rdata_start = 0x2c200
rdata_size = 0x13200
rdata = data[rdata_start:rdata_start+rdata_size]
strings = []
current = b''
for b in rdata:
    if 32 <= b <= 126:
        current += bytes([b])
    else:
        if len(current) >= 6:
            strings.append(current.decode('ascii'))
        current = b''
if len(current) >= 6:
    strings.append(current.decode('ascii'))

# Also extract from .text section
text_start = 0x400
text_size = 0x2be00
text_sec = data[text_start:text_start+text_size]
current = b''
for b in text_sec:
    if 32 <= b <= 126:
        current += bytes([b])
    else:
        if len(current) >= 6:
            s = current.decode('ascii')
            if any(c.isalpha() for c in s):
                strings.append(s)
        current = b''
if len(current) >= 6:
    s = current.decode('ascii')
    if any(c.isalpha() for c in s):
        strings.append(s)

with open(f'{OUT_DIR}/report/strings_pe.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total strings found: {len(strings)}\n")
    f.write("=" * 60 + "\n")
    for s in sorted(set(strings)):
        f.write(s + '\n')
print(f"Saved: strings_pe.txt ({len(strings)} strings)")

# === Step 3: Extract overlay zlib streams ===
print("\n=== Extracting overlay streams ===")
overlay = data[last_end:]
streams = []
pos = 0
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

print(f"Total zlib streams: {len(streams)}")

# Decompress all streams
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

decomp_text = bytes(all_decompressed).decode('latin-1')
print(f"Decompressed: {len(decomp_text)} chars")

# Save decompressed data
with open(f'{OUT_DIR}/src/decompressed_overlay.bin', 'wb') as f:
    f.write(all_decompressed)
print("Saved: decompressed_overlay.bin")

# Extract interesting strings from decompressed data
interesting = re.findall(r'[\x20-\x7e]{8,}', decomp_text)
with open(f'{OUT_DIR}/report/strings_overlay.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total strings found: {len(interesting)}\n")
    f.write("=" * 60 + "\n")
    for s in sorted(set(interesting)):
        f.write(s + '\n')
print(f"Saved: strings_overlay.txt ({len(interesting)} strings)")

# === Step 4: Extract Python co_code from PYZ-like structures ===
# The decompressed data contains Python marshal bytecode
# Look for type code 'c' (0x63 = code object) or 'C' (code)

# Try to find and save PYZ archive structure
pyz_idx = decomp_text.find('PYZ')
if pyz_idx >= 0:
    print(f"\n=== PYZ found at decompressed offset {pyz_idx} ===")
    # Save PYZ data
    pyz_data = all_decompressed[pyz_idx:pyz_idx+10000000]
    with open(f'{OUT_DIR}/src/pyz_archive.bin', 'wb') as f:
        f.write(pyz_data)
    print("Saved: pyz_archive.bin")

# === Step 5: Save config data ===
config_items = [
    'api_url', 'asset_wait', 'asset_delete_delay', 'reboot_wait', 'syslog_collect',
    'ifuse_mount_z', 'GUID_REGEX', 'BLDB_PATTERNS', 'max_attempts', 'MIN_ARCHIVE_SIZE',
    'POST_CONNECT_DELAY', 'CREATE_NO_WINDOW', 'global_GUID', 'mount_point',
    'BLDATABASE', 'BLDATABASEMANAGER', 'attempt_count', 'afc_mode', 'device_info',
    'iOS', 'guid', 'timeouts'
]
print("\n=== Configuration values ===")
with open(f'{OUT_DIR}/report/config.txt', 'w', encoding='utf-8') as f:
    for item in config_items:
        idx = decomp_text.find(item)
        if idx >= 0:
            start = max(0, idx - 60)
            end = min(len(decomp_text), idx + 80)
            snippet = decomp_text[start:end]
            clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in snippet)
            f.write(f"--- {item} ---\n{clean.strip()}\n\n")
            print(f"  {item} found")

print("Saved: config.txt")

# === Step 6: Extract Python module list ===
print("\n=== Python modules ===")
modules = set()
# Match .py or .pyc patterns with paths
for m in re.finditer(r'[a-zA-Z_][\w/]+\.py[c]?', decomp_text):
    path = m.group()
    if len(path) > 5 and not any(x in path for x in ['typeshed', 'third_party', '__pycache__']):
        modules.add(path)
with open(f'{OUT_DIR}/report/python_modules.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total Python modules: {len(modules)}\n")
    f.write("=" * 60 + "\n")
    for m in sorted(modules):
        f.write(m + '\n')
print(f"Saved: python_modules.txt ({len(modules)} modules)")

# === Step 7: Summary ===
print(f"\n{'='*50}")
print("EXTRACTION COMPLETE")
print(f"{'='*50}")
print(f"Output directory: {OUT_DIR}")
