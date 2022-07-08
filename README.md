# onesphere

OneSphere Open Source MOM(Manufacturing Operation Management) Solution

### 注意

1. MAC系统下开发，将启动参数中增加
    ```bash
    --limit-memory-hard=0
    
    ```

### 环境变量

```shell
ENV_TIMESCALE_ENABLE: false # 是否打开timescaledb支持
ENV_RUNTIME_ENV: dev # 运行时环境
ENV_ENABLE_SSO: false # 是否启用SSO功能
ENV_ONESHARE_EXPERIMENTAL_ENABLE: false # 是否开启实验性功能
ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL: false  # DAQ追踪码使用外键链接
ENV_OSS_BUCKET: oneshare
ENV_OSS_ENDPOINT: 127.0.0.1:9000
ENV_OSS_ACCESS_KEY: minio
ENV_OSS_SECRET_KEY: minio123
ENV_MAX_WORKERS: 8 # 并发获取外部数据时线程池的最大线性数量
ENV_OSS_SECURITY_TRANSPORT: false # 对象存储是否通过SSL连接

```

# 开发环境安装

```shell
git submodule update --init --recursive
sudo apt-get install -y libxml2-dev libxslt1-dev libsasl2-dev libldap2-dev libpq-dev build-essential libssl-dev
sudo apt-get install -y npm nodejs
sudo npm install -g rtlcss
```