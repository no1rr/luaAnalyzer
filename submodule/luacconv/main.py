import lua_tplink
import lua_ori
import argparse
import os
import logging



ORI_LUA    = 0
XIAOMI_LUA = 1
TPLINK_LUA = 2

def head_strip(data):
    if data[0] == b"#"[0]:
        return data[data.find(b'\n') + 1:]
    else:
        return data

def check_lua_type(dev_name):
    # if data.startswith(b"\x1bFate/Z\x1b"):  # xiaomi lua
    #     logging.warning("decode a xiaomi lua")
    #     return MI_LUA
    # elif data.startswith(b"\x1bLua"):
    #     logging.warning("decode a origin lua")
    #     return ORI_LUA
    # else:
    #     raise LuaDecodeException("unknown lua type")
    if dev_name == "tplink":
        return TPLINK_LUA
    elif dev_name == "xiaomi":
        return XIAOMI_LUA
    else:
        return ORI_LUA
    

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
    lua_type = check_lua_type(args.devname)

    if lua_type == TPLINK_LUA:
        header = lua_tplink.GlobalHead.parse(data)
        lua_tplink.lua_type_define(header)
        h = lua_tplink.Luac.parse(data)
    else:
        pass 
    
    if args.decode:
        print(h)
    else:
        if lua_type == TPLINK_LUA:
            # 32bit  
            lua_ori.lua_type_set(4, 4, 8, 4)
            h.global_head = lua_ori.GlobalHead.parse(
                bytes([0x1B, 0x4C, 0x75, 0x61, 0x51, 0x00, 0x01, 0x04, 0x04, 0x04, 0x08, 0x00]))
            d = lua_ori.Luac.build(h)
            with open(outfile_path, 'wb') as fp:
                fp.write(d)
    
