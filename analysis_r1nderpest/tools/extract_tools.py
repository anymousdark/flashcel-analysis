"""
Tools salvos para análise de PyInstaller / extração de R1nderPest
Criado durante análise forense de R1nderPest v2.4 (ZeroxDev)
"""
import zlib, struct, marshal, dis, os, sys, re

def find_overlay(exe_path):
    """Encontra overlay de um PE (PyInstaller)"""
    with open(exe_path, 'rb') as f:
        data = f.read()
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
    return data, last_end, data[last_end:]

def decompress_streams(data, max_streams=2000):
    """Decompress zlib streams from PyInstaller overlay"""
    streams = []
    pos = 0
    while pos < len(data) - 1:
        if data[pos] == 0x78 and data[pos+1] in (0x01, 0x5e, 0x9c, 0xda):
            streams.append(pos)
            pos += 2
        else:
            pos += 1
    print(f"Total streams: {len(streams)}")
    all_out = bytearray()
    for i in range(min(max_streams, len(streams)-1)):
        start = streams[i]
        end = streams[i+1] if i+1 < len(streams) else start + 200000
        try:
            dec = zlib.decompressobj()
            out = dec.decompress(data[start:end])
            all_out.extend(out)
        except:
            pass
    return bytes(all_out)

def extract_marshal_code(data, offset=0):
    """Try to extract Python marshal code objects from data"""
    results = []
    pos = offset
    while pos < len(data) - 10:
        if data[pos] == 0xe3:  # type 'code' in marshal 4+
            try:
                code_obj = marshal.loads(data[pos:pos+1000000])
                if hasattr(code_obj, 'co_filename'):
                    results.append((pos, code_obj))
                    # Skip past this code object
                    # Re-marshal it to find its size
                    try:
                        serialized = marshal.dumps(code_obj)
                        pos += len(serialized)
                        continue
                    except:
                        pass
            except:
                pass
        pos += 1
    return results

def extract_all_marshal(data):
    """Extract ALL marshal code objects from decompressed data"""
    codes = []
    pos = 0
    while pos < len(data) - 10:
        if data[pos] == 0xe3:  # type byte for code object
            # Use a conservative approach - try increasing sizes
            for size in [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]:
                try:
                    code_obj = marshal.loads(data[pos:pos+size])
                    if hasattr(code_obj, 'co_filename'):
                        serialized = marshal.dumps(code_obj)
                        codes.append((pos, len(serialized), code_obj))
                        pos += len(serialized) - 1
                        break
                except:
                    continue
        pos += 1
    return codes

def save_disassembly(code_obj, out_path):
    """Save disassembly of a code object"""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# File: {code_obj.co_filename}\n")
        f.write(f"# Name: {code_obj.co_name}\n")
        f.write(f"# First line: {code_obj.co_firstlineno}\n")
        f.write(f"# Arg count: {code_obj.co_argcount}\n")
        f.write(f"# Stack size: {code_obj.co_stacksize}\n")
        f.write(f"# Constants: {len(code_obj.co_consts)}\n")
        f.write(f"# Names: {len(code_obj.co_names)}\n")
        f.write(f"# Varnames: {len(code_obj.co_varnames)}\n")
        f.write(f"# Freevars: {len(code_obj.co_freevars)}\n")
        f.write(f"# Cellvars: {len(code_obj.co_cellvars)}\n")
        f.write("=" * 60 + "\n")
        dis.dis(code_obj, file=f)
        f.write("\n")
        # Also try to decompile with nested code objects
        for i, const in enumerate(code_obj.co_consts):
            if hasattr(const, 'co_code'):
                f.write(f"\n{'='*60}\n")
                f.write(f"# Nested: {const.co_name} @ {const.co_filename}:{const.co_firstlineno}\n")
                f.write(f"{'='*60}\n")
                dis.dis(const, file=f)

if __name__ == '__main__':
    print("=== PyInstaller Extraction Tools ===")
    print("Module loaded successfully")
