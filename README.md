convert custom luac to lua source. 

result may not be correct. 

ubuntu20.04, openjdk 17.0.11 2024-04-16

support device: tplink, teltonika, ubiquiti

tested: 

tplink archer c7, tplink archer ax21
        
teltonika RUT950, teltonika RUT230

ubiquiti airos

## Usage



```
python ./lua_analyzer.py -d ./squashfs-root -n device_name [-c]
```








## Credits

[mi_lua](https://github.com/zh-explorer/mi_lua/)

[unluac](https://github.com/HansWessels/unluac)
