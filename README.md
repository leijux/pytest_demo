# pytest_demo

本项目为 http api 和 web ui 测试的模板项目，测试对象 [gitea](https://gitea.com)

api 测试使用 httpx

ui 测试使用 playwright

> swagger：https://gitea.com/api/swagger

特点：

-   改进 allure step 支持 async 函数
-   提供 json schema 快照测试
-   allure 支持 playwright 的截图和录像
-   测试代码和测试数据分离
-   提供 cicd 集成脚本

## 项目说明

本项目在实现过程中，把整个项目拆分成请求方法封装、HTTP 接口封装、关键字封装、测试用例等模块。

首先利用 Python 把 HTTP 接口封装成 Python 接口，接着把这些 Python 接口组装成一个个的关键字，再把关键字组装成测试用例，而测试数据则通过 YAML 文件进行统一管理，然后再通过 Pytest 测试执行器来运行这些脚本，并结合 Allure 输出测试报告。

当然，如果感兴趣的话，还可以再对接口自动化进行 Jenkins 持续集成。

## 项目结构

```txt
├── 📁 core
│   ├── 📄 rest_client.py  http 请求封装
│   └── 📄 result_base.py  响应封装
├── 📁 models
│   ├── 📁 api             接口模型
│   └── 📁 ui              页面模型
├── 📁 operation           关键字封装
├── 📁 script              工具脚本
├── 📁 testcases           测试用例
├── 📁 utils               工具类
├── 📄 .env                环境变量
├── 📄 pyproject.toml      pytest 配置和依赖管理
└── 📄 Taskfile.yml        task 配置
```

## 项目部署

首先，下载项目源码后，安装 [task](https://taskfile.dev/) 和 [uv](https://docs.astral.sh/uv/) 工具。

```bash

task install //初始化环境
```

接着，修改 `testcases` 中的 `test_data.yaml` 文件，把 username 和 password 值修改为自己的配置。

```bash
task run-all-test //运行全部测试用例
```

## 测试报告效果展示

测试用例执行完毕后会在 `reports/allure_results` 中生成原始测试报告，使用如下命令自动打开浏览器展示 html 报告。

```bash
// 需要提前配置allure环境，才可以直接使用命令行
task show-repost
```

最终，可以看到测试报告的效果图如下：
![allure_report](/images/allure_report.png)
