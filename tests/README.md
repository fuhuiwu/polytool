# Polytool 测试套件

## 📁 测试文件

### 🤖 ChatBot 测试
- **chatbot.py** - ChatBot基础功能测试
  - 智能体创建和初始化
  - 多轮对话交互
  - 上下文记忆功能
  - 智能回复生成
  - 对话统计和导出

- **chat_interactive.py** - 交互式对话测试
  - API服务器集成测试
  - 实际对话流程验证
  - 响应格式检查

### 🧪 测试套件
- **run_all_tests.py** - 批量运行所有测试
  - 自动发现测试文件
  - 统一执行和结果汇总
  - UTF-8编码兼容

## 🚀 运行方式

### 单独运行测试
```bash
# ChatBot功能测试
python tests/chatbot.py

# 交互式对话测试
python tests/chat_interactive.py
```

### 批量运行所有测试
```bash
python tests/run_all_tests.py
```

## 📊 测试覆盖

- ✅ 智能体生命周期管理
- ✅ 对话历史和上下文
- ✅ 多会话支持
- ✅ 智能回复生成
- ✅ API服务器集成
- ✅ 错误处理机制
- ✅ 资源清理

## 💡 添加新测试

1. 在`tests/`目录下创建新的Python文件
2. 确保文件名不是`__init__.py`或`run_all_tests.py`
3. 测试套件会自动发现并执行新测试

## 🔧 测试环境

- **Python**: 3.10+
- **编码**: UTF-8
- **平台**: Windows/Linux/macOS
- **依赖**: 项目requirements.txt中的包