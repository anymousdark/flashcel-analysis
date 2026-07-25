import zlib, re, sys

with open(r'C:\R1nderpest\r1nderpest.exe', 'rb') as f:
    data = f.read()

overlay = data[0x44800:]

streams = []
pos = 0
while pos < len(overlay) - 1:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        streams.append(pos)
        pos += 2
    else:
        pos += 1

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
sys.stderr.write(f"Decompressed {count} streams, {len(text)} chars\n")

# Clean URLs
urls = re.findall(r'https?://[^\s"\'>);]+', text)
clean_urls = set()
for u in urls:
    cu = ''.join(c for c in u if 32 <= ord(c) <= 126)
    # Strip trailing non-url chars
    cu = re.sub(r'[^\w:/.\-~%?#@!$&()*+,;=]+$', '', cu)
    if len(cu) > 10 and 'http' in cu:
        clean_urls.add(cu)

print("=== URLs found ===")
for u in sorted(clean_urls):
    print(f"  {u}")

# IP:Port
ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
print("\n=== IP:Port found ===")
for ip in sorted(set(ips)):
    print(f"  {ip}")

# Print the new_r1nderpest code and surrounding
idx = text.find('new_r1nderpest')
if idx >= 0:
    start = max(0, idx - 3000)
    end = min(len(text), idx + 8000)
    section = text[start:end]
    for line in section.split('\n'):
        clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in line)
        if len(clean.strip()) > 5:
            print(clean)
