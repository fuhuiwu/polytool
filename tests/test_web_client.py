#!/usr/bin/env python3
"""
Web客户端功能测试脚本
"""

import requests
import time

def test_web_client():
    """测试Web客户端功能"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试Polytool Web客户端...")
    print(f"📍 基础URL: {base_url}")
    print()
    
    # 测试1: 访问聊天界面
    print("1️⃣ 测试聊天界面访问")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "Polytool ChatBot" in response.text:
            print("   ✅ 聊天界面可以正常访问")
        else:
            print(f"   ❌ 聊天界面访问失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    print()
    
    # 测试2: 静态文件服务
    print("2️⃣ 测试静态文件服务")
    static_files = [
        "/static/css/chat.css",
        "/static/js/chat.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {file_path} 可以正常访问")
            else:
                print(f"   ❌ {file_path} 访问失败，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {file_path} 请求失败: {e}")
    
    print()
    
    # 测试3: Chat API
    print("3️⃣ 测试Chat API")
    chat_data = {
        "message": "你好，我想测试一下Web客户端",
        "session_id": "web_test_session"
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("   ✅ Chat API正常工作")
                print(f"   📝 ChatBot回复: {result.get('response', '')[:100]}...")
            else:
                print(f"   ❌ Chat API返回错误: {result}")
        else:
            print(f"   ❌ Chat API请求失败，状态码: {response.status_code}")
            print(f"   📝 错误信息: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Chat API请求失败: {e}")
    
    print()
    
    # 测试4: 健康检查
    print("4️⃣ 测试健康检查")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 健康检查通过")
            print(f"   📊 智能体数量: {result.get('agents_count', 0)}")
        else:
            print(f"   ❌ 健康检查失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 健康检查请求失败: {e}")
    
    print()
    print("🎉 Web客户端测试完成!")
    print(f"🌐 请在浏览器中访问: {base_url}")
    print("💬 您可以与ChatBot进行实时对话交流!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Polytool ChatBot Web客户端测试")
    print("=" * 60)
    print()
    
    # 等待服务器完全启动
    print("⏳ 等待服务器完全启动...")
    time.sleep(2)
    
    test_web_client()