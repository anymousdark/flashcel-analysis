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
for i in range(min(800, len(streams)-1)):
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

# Find all configuration constants
config_items = [
    'api_url', 'asset_wait', 'asset_delete_delay', 'reboot_wait', 'syslog_collect',
    'ifuse_mount_z', 'GUID_REGEX', 'BLDB_PATTERNS', 'max_attempts', 'MIN_ARCHIVE_SIZE',
    'POST_CONNECT_DELAY', 'CREATE_NO_WINDOW', 'global_GUID', 'mount_point',
    'BLDATABASE', 'BLDATABASEMANAGER'
]

print("=== Configuration values ===")
# Look for patterns like: name = value or "name": value
for item in config_items:
    idx = text.find(item)
    if idx >= 0:
        start = max(0, idx - 50)
        end = min(len(text), idx + 80)
        snippet = text[start:end]
        clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in snippet)
        print(f"\n  {item}:")
        print(f"    {clean.strip()}")

# Look for version strings
print("\n=== Version strings ===")
for ver in re.finditer(r'\d+\.\d+(?:\.\d+)?(?: Release| beta| alpha)?', text):
    start = max(0, ver.start() - 30)
    end = min(len(text), ver.end() + 30)
    snippet = text[start:end]
    clean = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in snippet)
    print(f"  {clean.strip()}")

# Find all Python class names
print("\n=== Class/Function names ===")
classes = re.findall(r'class (\w+)', text)
for c in sorted(set(classes)):
    print(f"  class {c}")
funcs = re.findall(r'def (\w+)', text)
for f in sorted(set(funcs)):
    print(f"  def {f}")

# Find UI elements
print("\n=== UI Elements ===")
ui_items = ['QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit', 'QComboBox', 
            'QListWidget', 'QTableWidget', 'QTreeWidget', 'QProgressBar',
            'QTabWidget', 'QStackedWidget', 'QFrame', 'QGroupBox']
for ui in ui_items:
    count_ui = text.count(ui)
    if count_ui > 0:
        print(f"  {ui}: {count_ui} occurrences")
