#!/usr/bin/env python3
"""
HTTP服务器测试脚本
测试Polytool HTTP API端点是否正常工作
"""

import requests
import json
import sys
import time

def test_http_server():
    """测试HTTP服务器的各个端点"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试Polytool HTTP服务器...")
    print(f"📍 基础URL: {base_url}")
    print()
    
    # 测试1: 健康检查端点
    print("1️⃣ 测试健康检查端点 /health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        if response.status_code == 200:
            print("   ✅ 健康检查通过")
        else:
            print("   ❌ 健康检查失败")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    print()
    
    # 测试2: API文档端点
    print("2️⃣ 测试API文档端点 /docs")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API文档端点正常")
        else:
            print("   ❌ API文档端点失败")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 测试3: 聊天端点
    print("3️⃣ 测试聊天端点 /chat")
    chat_data = {
        "message": "你好，这是一个测试消息",
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat", 
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            print("   ✅ 聊天端点正常")
        else:
            print(f"   ❌ 聊天端点失败: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 测试4: 根端点
    print("4️⃣ 测试根端点 /")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            print("   ✅ 根端点正常")
        else:
            print("   ❌ 根端点失败")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    print("🎉 测试完成!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Polytool HTTP服务器测试")
    print("=" * 50)
    print()
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    test_http_server()