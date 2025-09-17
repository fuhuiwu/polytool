# ChatBot Agent 模块

## 🤖 简介

ChatBot是基于Polytool框架开发的智能聊天助手模块，具备以下特性：

- **💬 自然对话**: 支持流畅的中文对话交流
- **🧠 上下文记忆**: 记住对话历史，保持上下文连贯性
- **👥 多会话支持**: 支持多个独立的对话会话
- **🔧 智能响应**: 根据不同输入类型提供合适的回复
- **📊 对话统计**: 提供详细的对话信息和统计数据

## � 模块结构

```
chatbot/
├── __init__.py       # 模块入口，导出主要类
├── agent.py         # ChatBot智能体实现
├── conversation.py  # 对话管理组件
└── README.md        # 本文档
```

## 🚀 快速开始

### 1. 直接使用模块

```python
from agent.agents.chatbot import ChatBotAgent

# 创建ChatBot实例
chatbot = ChatBotAgent(
    agent_id="my_chatbot",
    name="我的ChatBot",
    description="个性化聊天助手"
)

# 初始化
await chatbot.initialize()

# 发送消息
response = await chatbot.process({
    "message": "你好！",
    "session_id": "session_001"
})

print(response["response"])
```

### 2. 通过API服务器使用

```bash
# 启动聊天模式
python api/server.py

# 选择聊天模式
选择运行模式:
1. 聊天模式 (chat)
2. 服务器模式 (server) - 暂未实现

请选择模式 [chat]: 1
```

### 3. 运行测试

```bash
# 功能测试
python tests/chatbot.py

# 交互测试  
python tests/chat_interactive.py
```

## 🏗️ 模块架构

### 核心组件

#### 1. ChatBotAgent (`agent.py`)
- **继承**: `Agent` 基类
- **功能**: 智能体核心实现
- **主要方法**:
  - `process()`: 处理用户输入并生成回复
  - `_generate_response()`: 生成智能回复
  - `_generate_smart_default_response()`: 智能默认回复逻辑
  - `get_conversation_info()`: 获取会话信息
  - `export_conversation()`: 导出对话历史

#### 2. ConversationManager (`conversation.py`)
- **功能**: 对话历史管理
- **特性**: 
  - 多会话支持
  - 历史记录限制
  - 消息添加和检索
- **主要方法**:
  - `add_message()`: 添加消息到会话
  - `get_conversation_history()`: 获取会话历史
  - `clear_conversation()`: 清空会话
  - `get_active_sessions()`: 获取活跃会话

#### 3. ChatMessage (`conversation.py`)
- **功能**: 聊天消息数据结构
- **属性**:
  - `role`: 消息角色 (user/assistant)
  - `content`: 消息内容
  - `timestamp`: 时间戳
- **方法**:
  - `to_dict()`: 转换为字典格式
  - `from_dict()`: 从字典创建消息
   - 提供生命周期管理
   - 支持依赖注入

2. **ChatBotAgent (聊天机器人智能体)**
   - 继承自Agent基类
   - 实现对话逻辑和上下文管理
   - 支持智能回复生成

3. **ConversationManager (对话管理器)**
   - 管理多会话对话历史
   - 提供消息存储和检索
   - 支持对话统计和导出

## 📝 使用示例

### 创建和使用ChatBot

```python
import asyncio
from agent.agents.chatbot import ChatBotAgent

async def example():
    # 创建ChatBot实例
    chatbot = ChatBotAgent()
    
    # 初始化
    await chatbot.initialize()
    
    # 发送消息
    input_data = {
        "message": "你好！",
        "session_id": "demo_session"
    }
    
    response = await chatbot.process(input_data)
    print(f"ChatBot: {response['response']}")
    
    # 清理资源
    await chatbot.cleanup()

# 运行示例
asyncio.run(example())
```

### 对话管理

```python
from agent.agents.chatbot import ConversationManager, ChatMessage

# 创建对话管理器
manager = ConversationManager()

# 添加消息
user_msg = ChatMessage("user", "你好")
assistant_msg = ChatMessage("assistant", "您好！")

manager.add_message("session_1", user_msg)
manager.add_message("session_1", assistant_msg)

# 获取对话历史
history = manager.get_conversation_history("session_1")
for msg in history:
    print(f"{msg.role}: {msg.content}")
```

## 🧪 测试

### 运行测试脚本

```bash
# 基础功能测试
python tests/chatbot.py

# 交互对话测试
python tests/chat_interactive.py
```

### 测试覆盖

- ✅ 智能体创建和初始化
- ✅ 多轮对话交互
- ✅ 上下文记忆功能
- ✅ 智能回复生成
- ✅ 对话统计和导出
- ✅ 多会话支持
- ✅ 资源清理

## 🎯 智能回复特性

ChatBot具备以下智能回复能力：

### 1. 问候语识别
- 输入: "你好", "您好", "hello", "hi"
- 响应: 友好的问候和自我介绍

### 2. 告别语识别
- 输入: "再见", "拜拜", "goodbye", "bye"
- 响应: 礼貌的告别语

### 3. 感谢语识别
- 输入: "谢谢", "感谢", "thank"
- 响应: "不客气！很高兴能帮助您..."

### 4. 自我介绍
- 输入: "你是谁", "介绍一下"
- 响应: 详细的自我介绍和功能说明

### 5. 功能询问
- 输入: "能做什么", "功能", "help"
- 响应: 功能列表和服务说明

### 6. 技术相关
- 输入: "polytool", "框架", "代码"
- 响应: 技术相关的专业回复

## 🔧 扩展开发

### 创建自定义智能体

```python
from agent.base import Agent

class MyCustomAgent(Agent):
    async def _initialize_agent(self):
        # 自定义初始化逻辑
        pass
    
    async def _cleanup_agent(self):
        # 自定义清理逻辑
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # 自定义处理逻辑
        return {"status": "success", "response": "自定义回复"}
```

### 注册和使用

```python
# 注册自定义智能体
agent_manager.register_agent(MyCustomAgent, "custom")

# 创建实例
agent = await agent_manager.create_agent(
    agent_type="custom",
    agent_id="my_agent",
    name="我的智能体"
)
```

## 📈 未来计划

- [ ] **LLM集成**: 集成OpenAI、Claude等大语言模型
- [ ] **RAG功能**: 集成检索增强生成能力
- [ ] **工具调用**: 支持外部工具和API调用
- [ ] **多模态**: 支持图像、音频等多模态输入
- [ ] **Web界面**: 提供Web聊天界面
- [ ] **持久化**: 对话历史持久化存储
- [ ] **插件系统**: 可扩展的插件架构

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 项目地址: [Polytool GitHub](https://github.com/your-org/polytool)
- 问题反馈: [GitHub Issues](https://github.com/your-org/polytool/issues)
- 文档说明: 查看项目根目录的README.md

---

**Polytool Framework** - 让AI开发更简单！🚀