#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web客户端测试脚本
===============

用于测试ChatBot Web客户端的功能
"""

import requests
import json

def test_chat_api():
    """测试聊天API"""
    url = "http://localhost:8000/chat"
    
    test_data = {
        "message": "你好，这是一个测试消息",
        "session_id": "test_session_123"
    }
    
    try:
        print("📤 发送测试消息...")
        print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"\\n📥 响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"\\n✅ 响应数据:")
            print(json.dumps(response_data, ensure_ascii=False, indent=2))
        else:
            print(f"\\n❌ 请求失败:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

def test_static_files():
    """测试静态文件访问"""
    files_to_test = [
        "/static/css/chat.css",
        "/static/js/chat.js"
    ]
    
    for file_path in files_to_test:
        url = f"http://localhost:8000{file_path}"
        try:
            print(f"\\n🔍 测试静态文件: {file_path}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 文件可访问，大小: {len(response.content)} bytes")
            else:
                print(f"❌ 文件访问失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 访问异常: {e}")

def main():
    """主函数"""
    print("🧪 开始Web客户端功能测试\\n")
    
    # 测试静态文件
    test_static_files()
    
    print("\\n" + "="*50)
    
    # 测试聊天API
    test_chat_api()
    
    print("\\n🏁 测试完成")

if __name__ == '__main__':
    main()