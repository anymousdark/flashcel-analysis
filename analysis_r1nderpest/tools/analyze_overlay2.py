import zlib, struct

with open(r'C:\R1nderpest\r1nderpest.exe', 'rb') as f:
    data = f.read()

overlay = data[0x44800:]

# Decompress all streams
results = []
pos = 0
total_decompressed = 0
count = 0

while pos < len(overlay) - 1 and count < 5000:
    if overlay[pos] == 0x78 and overlay[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
        try:
            decomp = zlib.decompress(overlay[pos:pos+200000])
            results.append((pos, len(decomp)))
            total_decompressed += len(decomp)
            pos += len(overlay) - len(zlib.compress(decomp))  # approximate
        except:
            pos += 1
        count += 1
    else:
        pos += 1

print(f"Decompressed {count} streams, total {total_decompressed} bytes")

# Find interesting strings in the decompressed data
all_text = []
pos = 0
for stream_pos, stream_len in results[:100]:
    try:
        decomp = zlib.decompress(overlay[stream_pos:stream_pos+200000])
        all_text.append(decomp)
    except:
        pass

combined = b''.join(all_text)
text = combined.decode('latin-1')

# Look for key terms
terms = ['http://', 'https://', 'api.', '.com.br', 'isalldone', 'palera1n', 'checkm8', 
         'bypass', 'icloud', 'unlock', 'iPhone', 'iPad', 'iOS', 'version', 'server']
for t in terms:
    idx = text.find(t)
    if idx >= 0:
        end = min(len(text), idx + 120)
        snippet = text[max(0,idx-10):end]
        print(f"\n'{t}' at decompressed offset {idx}: {repr(snippet)}")

# Also dump the "new_r1nderpest" Python script if found
idx = combined.find(b'new_r1nderpest')
if idx >= 0:
    print(f"\n\n=== Found 'new_r1nderpest' at decompressed offset {idx} ===")
    end = min(len(combined), idx + 5000)
    snippet = combined[idx:end]
    print(snippet.decode('latin-1'))
