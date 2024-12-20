convert custom luac to lua source. 

#### result may not be correct.  

support device: tplink, teltonika, ubiquiti

tested: 

tplink archer c7, tplink archer ax21
        
teltonika RUT950, teltonika RUT230

ubiquiti airos

## Environment

ubuntu20.04, openjdk 17.0.11 2024-04-16




## Usage

fill api_key of [Grok](https://console.x.ai/) and proxy(if needed) in config.yml first.

```
python ./lua_analyzer.py -d ./squashfs-root -n device_name [-l]
```








## Credits

[mi_lua](https://github.com/zh-explorer/mi_lua/)

[unluac](https://github.com/HansWessels/unluac)
