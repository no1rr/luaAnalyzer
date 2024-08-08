import yaml
import json
from posixpath import dirname
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from os.path import abspath, dirname
from inspect import getfile, currentframe
import requests
import os
import concurrent.futures
import subprocess

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=16)


def log(msg):
	print("[*] \033[0;31m{}\033[0m".format(msg))

def get_config(key):
    """Gets the value associated with a given key from a configuration file.

    Params:
    key (str): The key to look up in the configuration file.

    Returns:
    str: The value associated with the given key.
    """
    val = None
    path = "config.yml"
    
    try:
        with open('config.yml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            val = config[key]
    except:
        quit("load config err") 
    log("utils.get_config: "+key+": "+str(val) )
    return val

def get_url():
    return get_config("url")

def get_key():
    return get_config("api_key")

def get_proxy():
    return get_config("proxy") 

def get_model():
    return get_config("model") 

def make_request(url, headers=None, data=None, proxy_addr=None):
    """Makes API request

    Params:
    url (str): url to make request to
    headers (dict, optional): headers to send with request. Defaults to None.
    data (bytes, optional): data to send with request. Defaults to None.
    """
    if proxy_addr:
        proxy_handler = ProxyHandler({"http": proxy_addr, "https": proxy_addr})
        opener = build_opener(proxy_handler)

    request = Request(url, headers=headers or {}, data=data)
    try:
        if proxy_addr:
            with opener.open(request, timeout=10) as response:
                return response.read(), response
        else:
            with urlopen(request, timeout=10) as response:
                return response.read(), response

    except HTTPError as error:
        print(error.status, error.reason)
        quit("Exiting...")
    except URLError as error:
        print(error.reason)
        quit("Exiting...")
    except TimeoutError:
        print("Request timed out")
        quit("Exiting...")

def chat_q(message):
    """Sends a message to a chat model and returns the response.

    Params:
    message (str): The message to be sent to the chat model.

    Returns:
    str: The response content from the chat model.
    """
    pass


def get_lua_files(fs_dir):
    """Retrieves the paths of all Lua files in the specified directory.

    Params:
    fs_dir (str): The directory to search for Lua files.

    Returns:
    list: A list containing the paths of all found Lua files.
    """
    log("getting lua files' path: " + fs_dir)
    lua_files = os.popen(f"find {fs_dir} -name '*.lua'").read().split("\n")[:-1] 
    log("get lua file path ok")
    return lua_files

def get_files(fs_dir, pattern):
    log("get_files: "+fs_dir)
    files = os.popen(f"find {fs_dir} -name '{pattern}'").read().split("\n")[:-1] 
    return files

def dis_luac(path):
    """Disassembles a Luac file by using luadec 
    and saving the output to a .dec file.

    Params:
    path (str): The path to the Luac bytecode file to be disassembled.
    """
    cmd2 = "./mi_lua/tools/luadec -dis " + path + ".byte > " + path + ".dec" 
    subprocess.run(cmd2, shell=True, capture_output=True, text=True)
    log("dis file: %s ok"%path)

def disc_luac(path):
    """Discompiles a Lua bytecode file(.dec), 
    processes its content using GPT, 
    and writes the reconstructed source code to a .chat file.

    Params:
    path (str): The path to the Lua bytecode file to be processed.
    """
    bytecode_file_path = path + ".dec"
    chat_file_path     = path + ".chat"
    chat_file = open(chat_file_path, "w")
    data = None

    try:
        data = open(bytecode_file_path,"r").read()
    except:
        log("read dec file err: "+path)

    if data:
        # whole file data is too long for one chat, split to functions
        functions = data.split("\n\n\n")
        # skip header and function 0, which is function defination
        chat_file.write(functions[0])

        for code in functions[1:]:

            msg = '''下面是luadec还原的lua字节码，帮我还原成源代码。
            下面的代码是一个函数的代码，遇到字符串或者变量或者函数不要改变大小写,
            开头function给出函数名称。
            只需要给我lua代码就行，不要返回其他任何描述，
            也不要任何提示和注释。代码块不要用```包围。
            不要任何提示和注释。不要任何提示和注释。不要任何提示和注释。\n'''

            msg += "\n\n"+code
            lua_source = chat_q(msg)
            log("chat done: "+path)
            chat_file.write("\n\n"+lua_source+"\n\n")
            chat_file.flush()
    chat_file.close()
    log("discompile done: "+path)
    
def gen_psc_unluac(path):
    cmd = "java -jar ./submodule/unluac/src/unluac.jar " + path + ".correct > " + path + ".unluac"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    log("gen_psc_unluac: %s ok"%path)

def gen_psc_luadec(path):
    pass
def get_api_officallua(path):
    log("get_api: "+path)   
    lines = open(path, "r").read().split("\n")
    idx = 0
    eps = {}
    idx = 0
    while not lines[idx].startswith("  "):
        idx += 1
    
    
    while lines[idx].startswith("  "):
        while not lines[idx].endswith("  entry({"):
            print(lines[idx:])
            idx += 1
            if idx >= len(lines)-1:
                return eps

        ep1 = lines[idx+1].split("\"")[1]
        ep2 = lines[idx+2].split("\"")[1]
        ep3 = lines[idx+3].split("\"")[1]
        if "call" not in lines[idx+4]:
            idx += 1
            continue
        handler = lines[idx+4].split("\"")[1]
        #print(lines[idx:idx+5])
        endpt = ep1+"/"+ep2+"/"+ep3
        eps[endpt] = handler
        log(endpt + "  ->  "+handler)
        idx += 5
    
    return eps

def get_api_milua(path):
    pass

def save_api_data(dev_name, config_data):
    with open(f'api_{dev_name}.json', 'w', encoding='utf-8') as file:
        json.dump(config_data, file, ensure_ascii=False, indent=4)
    log("save_api_data: "+f'api_{dev_name}.json')

def get_apis(fs_dir, dev_name="test"):
    # find controller dir
    ctrl_dir = os.popen(f"find {fs_dir} -type d -name \"controller\"").read().split('\n')[0]
    log("get_apis: "+ctrl_dir)
    files = get_files(ctrl_dir, "*.lua.unluac")
    data = {}
    data["summary"] = {}
    for file in files:
        api_set = get_api_officallua(file)
        key = file.split("controller")[-1].split(".dis")[0]
        data["summary"][key] = len(api_set)
        data[key] = api_set
    save_api_data(dev_name, data)
    
def conv_luac_official(path):
    cmd = "python ./submodule/luacconv/main.py " + path + " -o " + path + ".correct" 
    subprocess.run(cmd, shell=True, capture_output=True, text=True)

def conv_luac_tplink(path):
    cmd = "python ./submodule/luacconv/main.py " + path + " -n tplink -o " + path + ".correct" 
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    log("convert file: %s ok"%path)

def conv_luac_xiaomi(path):
    print("conv_luac_xiaomi not acc")

convs = {'official': conv_luac_official,
        'xiaomi'   : conv_luac_xiaomi,
        'tplink'   : conv_luac_tplink
}



    