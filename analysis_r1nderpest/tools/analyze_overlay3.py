import zlib

with open(r'C:\R1nderpest\r1nderpest.exe', 'rb') as f:
    data = f.read()

overlay = data[0x44800:]

# Find all stream positions
streams = []
pos = 0
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

print(f"Total streams: {len(streams)}")
print(f"First 10 stream positions: {streams[:10]}")

# Decompress stream by stream using streaming decompressor
total_decomp = 0
all_data = bytearray()
count = 0

for i in range(min(200, len(streams)-1)):
    start = streams[i]
    end = streams[i+1] if i+1 < len(streams) else len(overlay)
    chunk = overlay[start:end]
    
    try:
        # zlib decompress, but we need to provide just the right amount of data
        # Use decompressobj to handle it
        dec = zlib.decompressobj()
        out = dec.decompress(chunk)
        # Check if there's leftover
        if dec.unconsumed_tail:
            # Stream wasn't fully contained, include more data
            extra = dec.unconsumed_tail + overlay[end:end+10000]
            out += dec.decompress(extra)
        all_data.extend(out)
        total_decomp += len(out)
        count += 1
    except Exception as e:
        pass

print(f"Decompressed {count} streams, total {total_decomp} bytes")

# Find interesting strings in all decompressed data
text = bytes(all_data).decode('latin-1')
print(f"\nDecoded text length: {len(text)}")

# Search for key terms
terms = ['http://', 'https://', 'api.', 'isalldone', 'palera1n', 'checkm8', 
         'bypass', 'iPhone', 'iPad', 'iOS', 'version', 'new_r1nderpest',
         'tornado', 'PyQt5', 'server', 'port', 'localhost']
for t in terms:
    idx = text.find(t)
    if idx >= 0:
        end = min(len(text), idx + 150)
        snippet = text[max(0,idx-30):end]
        print(f"\n'{t}' at offset {idx}:")
        print(f"  {repr(snippet)}")
