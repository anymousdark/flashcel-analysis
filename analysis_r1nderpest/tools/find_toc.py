"""
Find and extract the CArchive TOC from the raw overlay
"""
import zlib, struct, os

EXE_PATH = r'C:\R1nderpest\r1nderpest.exe'
OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\src'

with open(EXE_PATH, 'rb') as f:
    data = f.read()

# Find overlay
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

# Find all zlib streams
streams = []
pos = 0
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

print(f"Total zlib streams: {len(streams)}")
print(f"First stream at: {streams[0]}")
print(f"Last stream at: {streams[-1]}")
print(f"Overlay size: {len(overlay)}")

# Check what's between the last stream end and the end of file
last_stream_end = streams[-1]
# Find where this stream actually ends
# zlib stream ends when the decompressor says so
# Let me just check the last 100000 bytes of overlay for readable strings
tail_start = max(0, len(overlay) - 100000)
tail = overlay[tail_start:]

# Extract human-readable strings from tail
print(f"\n=== Readable strings in last 100KB of overlay (offset {tail_start}) ===")
current = b''
for b in tail:
    if 32 <= b <= 126:
        current += bytes([b])
    else:
        if len(current) >= 6:
            s = current.decode('ascii')
            print(f"  0x{tail_start + tail.find(current):x}: {s}")
        current = b''
if len(current) >= 6:
    s = current.decode('ascii')
    print(f"  0x{tail_start + tail.find(current):x}: {s}")

# Also check what's BETWEEN zlib streams - look at data at stream gaps
print(f"\n=== Non-zlib data between streams ===")
for i in range(min(20, len(streams)-1)):
    gap_end = streams[i+1]
    gap_start = streams[i]
    # Check if there's data between the end of stream i and start of stream i+1
    # Actually, zlib streams are concatenated, so the gap is 0
    if gap_end > gap_start:
        pass  # streams don't overlap

# Check what's AFTER the very last stream
# Actually, let me look at the structure differently
# The CArchive TOC is usually stored AFTER all the data, or at a known position
# For PyInstaller, the TOC is stored as the last entry in the archive

# Let me search for readable TOC entries near the end of file
end_data = data[max(0, len(data)-200000):]
text = end_data.decode('latin-1')

print(f"\n=== TOC entries near end of file ===")
# Look for the module names we know
known = ['mpyimod01_archive', 'mpyimod02_importers', 'mpyimod03_ctypes', 
         'mpyimod04_pywin32', 'pyiboot01_bootstrap', 'pyi_rth_inspect',
         'pyi_rth_traitlets', 'pyi_rth_pkgutil', 'pyi_rth_multiprocessing',
         'pyi_rth_pkgres', 'pyi_rth_setuptools', 'pyi_rth_cryptography_openssl',
         'pyi_rth_pyqt5', 'new_r1nderpest', 'IPython']

for name in known:
    # Search in the whole file
    idx = data.find(name.encode())
    if idx >= 0:
        # Show context: 20 bytes before
        ctx_start = max(0, idx - 30)
        ctx = data[ctx_start:idx+len(name)+30]
        print(f"\n  '{name}' at 0x{idx:x}:")
        # Show hex of surrounding
        hex_str = ' '.join(f'{ctx[i]:02x}' for i in range(min(60, len(ctx))))
        ascii_str = ''.join(chr(ctx[i]) if 32 <= ctx[i] <= 126 else '.' for i in range(min(60, len(ctx))))
        print(f"    {hex_str}")
        print(f"    {ascii_str}")
