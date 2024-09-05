import utils 
import argparse
import concurrent.futures
from tqdm import tqdm


thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=utils.get_config("thread_count"))

def banner():
    print('''
     _                                  _                    
| |               /\               | |                   
| |_   _  __ _   /  \   _ __   __ _| |_   _ _______ _ __ 
| | | | |/ _` | / /\ \ | '_ \ / _` | | | | |_  / _ \ '__|
| | |_| | (_| |/ ____ \| | | | (_| | | |_| |/ /  __/ |   
|_|\__,_|\__,_/_/    \_\_| |_|\__,_|_|\__, /___\___|_|   
                                       __/ |             
                                      |___/
                                      ''')
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #disa_group = parser.add_mutually_exclusive_group(required=True)
    disc_group = parser.add_mutually_exclusive_group()

    parser.add_argument('-fs_dir', '-d', type=str, help="firm filesystem directory", required=True)

    # disa_group.add_argument('-use_unluac', '-u', action='store_true', help='use unluac to disassembly')
    # disa_group.add_argument('-use_luadec', '-l', action='store_true', help='use luadec to disassembly')
    
    disc_group.add_argument('-use_chat', '-c', action='store_true', help='use chatgpt to discompile')
    disc_group.add_argument('-use_script', '-s', action='store_true', help='use custom script to discompile')

    parser.add_argument('-dev_name', '-n', type=str, choices=utils.support_devices, help='device name', required=True)
    args = parser.parse_args()

    banner()

    files = utils.get_lua_files(args.fs_dir)

    # step1. convert bytecode 
    print("step1. convert bytecode")
    tasks = [thread_pool.submit(utils.conv_luac, args.dev_name ,file) for file in files]
    for _ in tqdm(concurrent.futures.as_completed(tasks), total=len(tasks)):
        pass
    #concurrent.futures.wait(tasks)
    
    # step2. generate lua pseudocode
    print("step2. generate lua pseudocode")
    tasks = [thread_pool.submit(utils.gen_psc_unluac, file) for file in files]
    for _ in tqdm(concurrent.futures.as_completed(tasks), total=len(tasks)):
        pass
    
    # step3. generate lua source code
    print("step3. generate lua source code")
    '''
    [TODO] fill fields in config.yaml first.
    '''
    if args.use_chat:
        tasks = [thread_pool.submit(utils.disc_luac, file) for file in files]
        for _ in tqdm(concurrent.futures.as_completed(tasks), total=len(tasks)):
            pass

    else:
        print("script not acc")
    



    



    

    