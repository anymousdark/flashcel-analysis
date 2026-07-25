import zlib, re, sys

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

# Decompress up to 500 streams
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

# Use latin-1 to avoid encoding errors
text = bytes(all_data).decode('latin-1')
print(f"Decompressed {count} streams, {len(text)} chars", file=sys.stderr)

# Find clean URLs - filter out non-printable chars
def clean_url(m):
    url = m.group(0)
    clean = ''.join(c for c in url if 32 <= ord(c) <= 126)
    return clean if len(clean) > 10 else ''

urls = re.findall(r'https?://[^\s"\'>);]+', text)
clean_urls = set()
for u in urls:
    cu = clean_url(u)
    if cu and len(cu) > 10:
        clean_urls.add(cu)

print(f"\n=== URLs found ===")
for u in sorted(clean_urls):
    print(f"  {u}")

# IP:Port
ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
print(f"\n=== IP:Port found ===")
for ip in sorted(set(ips)):
    print(f"  {ip}")

# Extract Python code around new_r1nderpest
idx = text.find('new_r1nderpest')
if idx >= 0:
    print(f"\n=== Code around new_r1nderpest ===", file=sys.stderr)
    start = max(0, idx - 3000)
    end = min(len(text), idx + 8000)
    section = text[start:end]
    out_lines = []
    for line in section.split('\n'):
        clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in line)
        if len(clean.strip()) > 5:
            out_lines.append(clean)
    print('\n'.join(out_lines[-200:]))
