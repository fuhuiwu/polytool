# Polytool

一个通用智能体框架，基于低代码开发、插件化架构和增强RAG技术构建。

## 🚀 新功能: ChatBot智能体

Polytool现在内置了一个功能完整的ChatBot智能体，支持命令行和Web界面两种交互方式！

### ✨ ChatBot特性
- 💬 自然中文对话交流
- 🧠 智能上下文记忆
- 👥 多会话支持  
- 🎯 智能回复生成
- 📊 对话统计分析
- 🌐 **现代化Web界面**
- 📱 响应式设计，支持移动端

### 🎮 快速体验

#### Web界面（推荐）
```bash
# 启动HTTP服务器
python main.py --mode http

# 访问Web聊天界面
# 浏览器打开: http://localhost:8000/chat-ui
```

#### 命令行模式
```bash
# 启动交互式ChatBot
python main.py --debug

# 或运行测试脚本
python tests/chat_interactive.py
```

### 🌟 Web ChatBot功能

- **🎨 现代化界面**: 精美的聊天UI设计，支持深色/浅色主题
- **⚡ 实时对话**: 流畅的消息发送和接收体验
- **📱 响应式设计**: 完美适配桌面和移动设备
- **🔧 丰富功能**: 
  - 快捷消息按钮
  - 字符计数器
  - 连接状态显示
  - 设置面板
  - 消息时间戳
  - 声音通知（可选）
- **🛡️ 稳定可靠**: 完善的错误处理和用户反馈

### 📚 API接口

Web ChatBot提供标准的REST API：

```bash
# 发送聊天消息
POST /chat
Content-Type: application/json

{
  "message": "你好，请介绍一下自己",
  "session_id": "my_session"
}
```

详细使用指南请查看 [ChatBot使用指南](CHATBOT_GUIDE.md)

## 项目结构

```
polytool/
├── agent/                # 智能体层
│   ├── base.py          # 智能体基类
│   └── agents/          # 具体智能体实现
├── orchestration/       # 管理层
│   ├── llm_gateway.py   # LLM网关
│   ├── memory_manager.py # 记忆与知识库管理
│   └── tool_gateway.py  # 工具统一API服务
├── resource/           # 资源层
│   ├── models/         # 大模型适配
│   ├── memory/         # 记忆与知识库
│   └── plugins/        # 第三方插件与工具
├── api/               # 对外API
│   ├── http_server.py  # FastAPI HTTP服务器
│   └── simple_http_server.py # 简单HTTP服务器
├── web/               # Web界面
│   ├── templates/      # HTML模板
│   │   └── chat.html  # 聊天界面
│   └── static/        # 静态资源
│       ├── css/       # 样式文件
│       └── js/        # JavaScript文件
├── config/            # 配置管理
├── utils/             # 工具函数
├── tests/             # 单元测试
└── main.py           # 启动入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制并编辑环境配置文件：

```bash
cp .env.example .env
# 编辑.env文件，配置API密钥等参数
```

### 3. 启动应用

#### Web模式（推荐）
```bash
python main.py --mode http
```
启动后访问Web界面：
- 聊天界面: http://localhost:8000/chat-ui  
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

#### 调试模式
```bash
python main.py --debug
```

#### 标准模式
```bash
python main.py
```

### 4. 访问应用

- **Web聊天界面**: http://localhost:8000/chat-ui
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 命令行选项

- `--config, -c`: 指定配置文件路径
- `--debug, -d`: 启用调试模式  
- `--mode, -m`: 启动模式 (http/debug/console)
- `--port, -p`: 指定端口号
- `--host`: 指定主机地址
- `--version, -v`: 显示版本信息

## 功能特性

- 🚀 **低代码开发**: 通过配置和拖拽快速构建AI应用
- 🔌 **插件化架构**: 支持模型和工具的即插即用
- 🧠 **增强RAG**: 提供上下文感知和记忆增强功能
- 🌐 **统一API**: 屏蔽不同LLM和工具的接口差异
- � **Web ChatBot**: 现代化的聊天界面，支持实时对话
- 📱 **响应式设计**: 完美适配桌面和移动设备
- 🎨 **主题支持**: 深色/浅色主题切换
- �📊 **可观测性**: 全链路监控和日志审计
- 🔒 **企业级**: 安全认证、权限控制和合规支持
- ⚡ **高性能**: 优化的HTTP服务器和异步处理

## 开发指南

TODO: 添加详细的开发文档和示例

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 贡献

欢迎提交Issues和Pull Requests来帮助改进项目！

## 联系方式

- GitHub: [fuhuiwu](https://github.com/fuhuiwu)
- 项目地址: [polytool](https://github.com/fuhuiwu/polytool)