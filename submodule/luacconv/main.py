import lua_tplink
import lua_teltonika
import lua_ubiquiti
import lua_xiaomi
import lua_ori
import argparse
import os
import logging


convs = {
    "tplink"       : lua_tplink,
    "teltonika"    : lua_teltonika,
    "ubiquiti"     : lua_ubiquiti,
    "xiaomi"       : lua_xiaomi
} 

def head_strip(data):
    if data[0] == b"#"[0]:
        return data[data.find(b'\n') + 1:]
    else:
        return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="translate luac with xiaomi and origin")
    parser.add_argument("infile", type=str)
    parser.add_argument("-o", dest="outfile", help="out put file", type=str, nargs="?")
    parser.add_argument("-n", dest="devname", help="device name", type=str, nargs="?")
    parser.add_argument("-d", dest="decode", help="only decode luac and print content", action="store_true")

    args = parser.parse_args()
    if not os.path.isfile(args.infile):
        raise LuaDecodeException("The infile is not a regular file")
    infile_path = args.infile
    outfile_path = args.outfile
    if outfile_path is None:
        outfile_path = infile_path + ".dec"

    with open(infile_path, 'rb') as fp:
        data = fp.read()
    
    data = head_strip(data)

    lua_conv = convs[args.devname]
    header = lua_conv.GlobalHead.parse(data)
    lua_conv.lua_type_define(header)
    h = lua_conv.Luac.parse(data)
    
    if args.decode:
        print(h)
    else:
        # 32 bit
        if header.size_size_t == 4:
            lua_ori.lua_type_set(4, 4, 8, 4)
            h.global_head = lua_ori.GlobalHead.parse(
                bytes([0x1B, 0x4C, 0x75, 0x61, 0x51, 0x00, 0x01, 0x04, 0x04, 0x04, 0x08, 0x00]))
            d = lua_ori.Luac.build(h)
            with open(outfile_path, 'wb') as fp:
                fp.write(d)
    
    
