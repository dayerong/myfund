# myfund
自选基金实时估值查询

* 在fund.ini文件中添加自选基金的基金代码

```
003834
160219
163115
```

* config.ini设置透明度与请求数据时间 
```
[configuration]
flush_time = 60     # 请求基金接口的时间
WindowOpacity = 0.3 # 透明度
```


* 用pyinstaller打包成exe
<img src="https://raw.githubusercontent.com/dayerong/myfund/main/snapshot.png">
