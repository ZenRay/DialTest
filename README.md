# 说明
该项目是针对播测开发中的项目进行重构

# 项目结构
```
source/
├── __init__.py
├── app
│   ├── communicator
│   │   ├── UI
│   ├── config
│   └── utils
│       ├── _error_codes.py
│       ├── _key_codes.py
│       ├── adb.py
│       ├── check.py
│       ├── config.py
│       └── service
│           ├── _base.py
│           ├── _execute_check.py
│           ├── _execute_task.py
│           ├── _request_task.py
│           ├── heatbeat.py
│           └── report.py
└── temp
```

重构 app 的应用模块主要包括拆分为：
* communicator 播测应用的界面接口
* config 播测的配置信息，包括存储播测设备的配置信息（可以加载相关配置信息）、提交结果的数据的接口配置信息
* utils 提供各种服务模块，报告、心跳的服务接口，其他测试的基本例如 adb 命令调用、配置读取与写入。此外还有统一管理的错误 protocol
* temp 用于存储日志信息

# 用例
## 配置调整
项目集成在 [main.py](./main.py) 中完成。*接口相关的 IP 地址需要配置*，可以在 `source/app/config/url.txt` 中添加 IP，另外可以直接修改 [api.ini](./source/app/config/api.ini) 和 [report.ini](./source/app/config/report.ini) 两个文件中链接信息。
## 启动服务
使用 `python main.py` 启动服务，点击界面按钮启动相关服务