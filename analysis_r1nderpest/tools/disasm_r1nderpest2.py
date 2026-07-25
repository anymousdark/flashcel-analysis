"""
Better marshal extraction - find all \xe3 positions and try each
"""
import sys, os, marshal, dis, struct

OUT_DIR = r'C:\Users\Aycher\Documents\Default Project\analysis_r1nderpest\src'
DESKTOP_DIR = r'C:\Users\Aycher\Desktop\R1nderPest_Cracked\src'

with open(f'{OUT_DIR}/decompressed_all.bin', 'rb') as f:
    data = f.read()

# Find all bytes that could be marshal type codes
# Type code 'c' = \xe3 for code object in Python 3.8+ (type 'code' = 0xe3)
# Earlier Python uses type 0x63 for code objects
# In Python 3.13, the type flag for code objects is 'c' = 0x63

# Let me check what types Python 3.13 uses for marshal
import types
code = compile("x=1", "<test>", "exec")
ser = marshal.dumps(code)
print(f"Type byte for code object: 0x{ser[0]:02x} (expected 0xe3 for 3.8+, 0x63 for 3.4+)")
print(f"Python version: {sys.version}")

# In Python 3.13, marshal type for code is 0xe3 ('c' flag)
# Let me search for 0xe3
target_type = 0xe3

# Find all potential code object positions
positions = []
pos = 0
while pos < len(data) - 10:
    if data[pos] == target_type:
        positions.append(pos)
        pos += 1
    else:
        pos += 1

print(f"Found {len(positions)} potential code object positions")

# Try each position
codes = []
for pos in positions:
    # Try to read a code object of various possible sizes
    for max_size in [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]:
        try:
            obj = marshal.loads(data[pos:pos+max_size])
            if hasattr(obj, 'co_filename') and hasattr(obj, 'co_code'):
                serialized = marshal.dumps(obj)
                codes.append((pos, len(serialized), obj))
                break
        except:
            continue

print(f"Found {len(codes)} valid code objects")

# Save all
seen_files = set()
out_path = os.path.join(OUT_DIR, 'full_disassembly.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f"# R1nderPest - Python Bytecode Disassembly\n")
    f.write(f"# Total: {len(codes)} code objects\n\n")
    
    for pos, size, code in codes:
        f.write(f"\n{'#'*60}\n")
        f.write(f"# Offset: {pos}, Size: {size}\n")
        f.write(f"# File: {code.co_filename}\n")
        f.write(f"# Name: {code.co_name}\n")
        f.write(f"# Line: {code.co_firstlineno}\n")
        f.write(f"# Args: {code.co_argcount}, Stack: {code.co_stacksize}\n")
        f.write(f"# Vars: {len(code.co_varnames)}, Consts: {len(code.co_consts)}\n")
        f.write(f"{'#'*60}\n")
        dis.dis(code, file=f)
        f.write("\n")
        seen_files.add(code.co_filename)

print(f"Saved: full_disassembly.txt")
print(f"Files referenced: {len(seen_files)}")
for fn in sorted(seen_files):
    print(f"  {fn}")

# Extract new_r1nderpest code object specifically
for pos, size, code in codes:
    if 'new_r1nderpest' in code.co_filename:
        new_path = os.path.join(OUT_DIR, 'new_r1nderpest_disasm.txt')
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(f"# {code.co_filename}\n")
            f.write(f"# Name: {code.co_name}\n")
            f.write(f"# Line: {code.co_firstlineno}\n")
            f.write(f"{'='*60}\n")
            dis.dis(code, file=f)
        print(f"Saved: new_r1nderpest_disasm.txt")
        break

# Copy to desktop
import shutil
for fname in ['full_disassembly.txt', 'new_r1nderpest_disasm.txt']:
    src = os.path.join(OUT_DIR, fname)
    dst = os.path.join(DESKTOP_DIR, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {fname} to desktop")
