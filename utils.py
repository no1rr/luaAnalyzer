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
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=16)


def log(msg):
    pass
	#print("[*] \033[0;31m{}\033[0m".format(msg))

def get_config(key):
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
    output = llm([HumanMessage(content=message)])
    return output.content


def get_lua_files(fs_dir):
    log("getting lua files' path: " + fs_dir)
    lua_files = os.popen(f"find {fs_dir} -name '*.lua'").read().split("\n")[:-1] 
    log("get lua file path ok")
    return lua_files

llm = ChatOpenAI(
    streaming=True,
    verbose=True,
    openai_api_key=get_config("api_key"),
    openai_api_base=get_config("base_url"),  
    model_name=get_config("model")
)

def disc_luac(path):
    bytecode_file_path = path + ".unluac"
    chat_file_path     = path + ".chat.lua"
    chat_file = open(chat_file_path, "w")
    data = None

    try:
        data = open(bytecode_file_path,"r").read()
    except:
        log("read dec file err: "+path)

    if data:
        # whole file data is too long for one chat, split to functions
        functions = data.split("\nfunction ")
        # skip header and function 0, which is function defination
        # chat_file.write(functions[0])
        global_vars = True
        for code in functions:

            msg = '''下面是unluac还原的lua字节码，帮我还原成源代码，并把其中的变量重命名成合适变量名。\n\n'''
            if global_vars:
                global_vars = False
            else:
                msg += "function "

            msg += code
            lua_source = chat_q(msg).split("```lua")[1].split("```")[0]
            log("chat done: "+path)
            chat_file.write(lua_source+"\n")
            chat_file.flush()
    else:
        log("disc_luac: data empty, maybe lua source; "+path)
    chat_file.close()
    log("disc_luac: discompile done: "+path)
    
def gen_psc_unluac(path):
    cmd = "java -jar ./submodule/unluac/src/unluac.jar " + path + ".correct > " + path + ".unluac"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    log("gen_psc_unluac: %s ok"%path)
    
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





    