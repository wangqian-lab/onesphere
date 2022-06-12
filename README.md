# onesphere

OneSphere Open Source MOM(Manufacturing Operation Management) Solution

### 注意

1. MAC系统下开发，将启动参数中增加
    ```bash
    --limit-memory-hard=0
    
    ```

### 环境变量

```shell
ENV_ENABLE_SSO: false # 是否启用SSO功能
ENV_ONESHARE_EXPERIMENTAL_ENABLE: false # 是否开启实验性功能
ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL: false  # DAQ追踪码使用外键链接

```

# 安装

```shell
git submodule update --init --recursive

```