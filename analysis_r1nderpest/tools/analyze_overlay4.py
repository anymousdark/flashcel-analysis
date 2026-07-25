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

# Decompress more streams (up to 500)
all_data = bytearray()
count = 0

for i in range(min(500, len(streams)-1)):
    start = streams[i]
    end = streams[i+1] if i+1 < len(streams) else start + 200000
    chunk = overlay[start:end]
    
    try:
        dec = zlib.decompressobj()
        out = dec.decompress(chunk)
        all_data.extend(out)
        count += 1
    except:
        pass

text = bytes(all_data).decode('latin-1')
print(f"Decompressed {count} streams, {len(text)} chars")

# Search for ALL URLs
import re
urls = re.findall(r'https?://[^\s"\'>)]+', text)
print(f"\n=== URLs found ===")
for u in sorted(set(urls)):
    print(f"  {u}")

# Search for the IP:port
ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
print(f"\n=== IP:Port found ===")
for ip in sorted(set(ips)):
    print(f"  {ip}")

# Extract the main Python script context
idx = text.find('new_r1nderpest.py')
if idx >= 0:
    print(f"\n=== Code around new_r1nderpest.py ===")
    start = max(0, idx - 2000)
    end = min(len(text), idx + 5000)
    section = text[start:end]
    # Filter to printable lines
    for line in section.split('\n'):
        # Clean up non-printable
        clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in line)
        if len(clean.strip()) > 10:
            print(clean)

# Find the "194.99.21.156" context
ip_idx = text.find('194.99.21.156')
if ip_idx >= 0:
    print(f"\n=== Context around C2 server ===")
    start = max(0, ip_idx - 1000)
    end = min(len(text), ip_idx + 5000)
    section = text[start:end]
    for line in section.split('\n'):
        clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in line)
        if len(clean.strip()) > 10:
            print(clean)
