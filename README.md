convert custom luac to lua source. 

result may not be correct. 

ubuntu20.04, jdk17

support device: tplink

tested: tplink archer c7, tplink archer ax21



## Usage

do not use gpt.

```
python ./lua_analyzer.py -d ./squashfs-root -n tplink
```


use gpt.

```
python ./lua_analyzer.py -d ./squashfs-root -c -n tplink
```





## Credits

[mi_lua](https://github.com/zh-explorer/mi_lua/)

[unluac](https://github.com/HansWessels/unluac)