import zlib, struct

with open(r'C:\R1nderpest\r1nderpest.exe', 'rb') as f:
    data = f.read()

overlay_start = 0x44800
overlay = data[overlay_start:]

# Count zlib streams
pos = 0
streams = []
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

print(f"Total zlib streams: {len(streams)}")
print(f"First 20: {streams[:20]}")

# Try decompressing first stream
print("\n=== Trying decompression of first stream ===")
try:
    decomp = zlib.decompress(overlay[:200000])
    print(f"Decompressed {len(decomp)} bytes")
    text = decomp.decode('utf-8', errors='replace')
    print(f"First 1000 chars:\n{text[:1000]}")
except Exception as e:
    print(f"Full decompress failed: {e}")
    # Try smaller chunk
    try:
        decomp = zlib.decompress(overlay[:10000])
        print(f"Decompressed 10K: {len(decomp)} bytes")
        print(decomp[:500].decode('utf-8', errors='replace'))
    except:
        print("Even 10K failed")
