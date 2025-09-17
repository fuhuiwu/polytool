/**
 * Polytool ChatBot Web Client
 * 聊天界面交互逻辑
 */

class PolytoolChatClient {
    constructor() {
        // 初始化配置
        this.config = {
            apiEndpoint: '/chat',
            sessionId: this.generateSessionId(),
            autoScroll: true,
            showTimestamp: true,
            soundEnabled: false,
            maxRetries: 3,
            retryDelay: 1000
        };

        // 状态管理
        this.state = {
            isConnected: true,
            isLoading: false,
            messageCount: 0,
            currentTheme: 'light'
        };

        // DOM 元素引用
        this.elements = {};
        
        // 初始化应用
        this.init();
    }

    /**
     * 初始化应用
     */
    async init() {
        try {
            this.initElements();
            this.initEventListeners();
            this.loadSettings();
            this.updateConnectionStatus();
            
            console.log('✅ Polytool ChatBot Client 初始化成功');
        } catch (error) {
            console.error('❌ 初始化失败:', error);
            this.showError('应用初始化失败，请刷新页面重试');
        }
    }

    /**
     * 初始化DOM元素引用
     */
    initElements() {
        const elementIds = [
            'message-input', 'send-btn', 'messages-container', 'char-counter',
            'connection-status', 'clear-chat', 'toggle-theme', 'settings-btn',
            'settings-panel', 'close-settings', 'session-id', 'auto-scroll',
            'show-timestamp', 'sound-enabled', 'loading-indicator', 
            'error-toast', 'success-toast', 'error-message', 'success-message',
            'close-error'
        ];

        // 记录找不到的元素
        const missingElements = [];

        elementIds.forEach(id => {
            const element = document.getElementById(id);
            const key = id.replace(/-/g, '_');  // 修复正则表达式
            this.elements[key] = element;
            
            if (!element) {
                missingElements.push(id);
            }
        });

        // 输出调试信息
        if (missingElements.length > 0) {
            console.warn('以下元素未找到:', missingElements);
        }

        // 检查必需元素
        if (!this.elements.message_input || !this.elements.send_btn) {
            const missing = [];
            if (!this.elements.message_input) missing.push('message-input');
            if (!this.elements.send_btn) missing.push('send-btn');
            throw new Error(`必需的DOM元素不存在: ${missing.join(', ')}`);
        }
    }

    /**
     * 初始化事件监听器
     */
    initEventListeners() {
        // 输入框事件
        this.elements.message_input.addEventListener('input', (e) => {
            this.handleInputChange(e);
        });

        this.elements.message_input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 发送按钮
        this.elements.send_btn.addEventListener('click', () => {
            this.sendMessage();
        });

        // 头部按钮
        if (this.elements.clear_chat) {
            this.elements.clear_chat.addEventListener('click', () => {
                this.clearChat();
            });
        }

        if (this.elements.toggle_theme) {
            this.elements.toggle_theme.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        if (this.elements.settings_btn) {
            this.elements.settings_btn.addEventListener('click', () => {
                this.toggleSettings();
            });
        }

        // 设置面板
        if (this.elements.close_settings) {
            this.elements.close_settings.addEventListener('click', () => {
                this.closeSettings();
            });
        }

        // 快捷操作按钮
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-btn')) {
                const message = e.target.getAttribute('data-message');
                if (message && this.elements.message_input) {
                    this.elements.message_input.value = message;
                    this.sendMessage();
                }
            }
        });

        // 错误提示关闭
        if (this.elements.close_error) {
            this.elements.close_error.addEventListener('click', () => {
                this.hideError();
            });
        }

        // 设置变更监听
        ['auto_scroll', 'show_timestamp', 'sound_enabled'].forEach(setting => {
            if (this.elements[setting]) {
                this.elements[setting].addEventListener('change', () => {
                    this.saveSettings();
                });
            }
        });

        if (this.elements.session_id) {
            this.elements.session_id.addEventListener('change', (e) => {
                this.config.sessionId = e.target.value || this.generateSessionId();
                this.saveSettings();
            });
        }
    }

    /**
     * 发送消息
     */
    async sendMessage() {
        // 检查必需元素
        if (!this.elements.message_input) {
            console.error('输入框元素不存在');
            this.showError('界面初始化失败，请刷新页面');
            return;
        }
        
        const message = this.elements.message_input.value.trim();
        if (!message || this.state.isLoading) return;

        try {
            // 显示用户消息
            this.displayMessage('user', message);
            
            // 清空输入框
            this.elements.message_input.value = '';
            this.updateCharCounter();
            this.updateSendButton();

            // 显示加载状态
            this.setLoading(true);

            // 发送API请求
            const response = await this.sendApiRequest(message);
            
            // 显示机器人回复
            this.displayMessage('bot', response.response, {
                timestamp: response.timestamp,
                conversationLength: response.conversation_length
            });

            // 播放提示音
            if (this.config.soundEnabled) {
                this.playNotificationSound();
            }

        } catch (error) {
            console.error('发送消息失败:', error);
            this.showError(`发送失败: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * 发送API请求
     */
    async sendApiRequest(message, retryCount = 0) {
        try {
            const requestData = {
                message: message,
                session_id: this.config.sessionId,
                context: {}
            };

            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(data.message || 'API返回错误状态');
            }

            this.updateConnectionStatus(true);
            return data;

        } catch (error) {
            this.updateConnectionStatus(false);
            
            // 重试逻辑
            if (retryCount < this.config.maxRetries) {
                await this.delay(this.config.retryDelay * (retryCount + 1));
                return this.sendApiRequest(message, retryCount + 1);
            }
            
            throw error;
        }
    }

    /**
     * 显示消息
     */
    displayMessage(type, content, options = {}) {
        // 确保消息容器存在
        if (!this.elements.messages_container) {
            console.error('消息容器不存在，无法显示消息');
            return;
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        messageElement.innerHTML = this.createMessageHTML(type, content, options);
        
        // 添加动画
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(10px)';
        
        this.elements.messages_container.appendChild(messageElement);
        
        // 触发动画
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });

        // 自动滚动
        if (this.config.autoScroll) {
            this.scrollToBottom();
        }

        this.state.messageCount++;
    }

    /**
     * 创建消息HTML
     */
    createMessageHTML(type, content, options = {}) {
        const avatar = type === 'user' 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-robot"></i>';
        
        const timestamp = options.timestamp 
            ? new Date(options.timestamp).toLocaleTimeString('zh-CN')
            : new Date().toLocaleTimeString('zh-CN');

        const timeDisplay = this.config.showTimestamp 
            ? `<div class="message-time"><span>${timestamp}</span></div>` 
            : '';

        return `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(content)}</div>
                ${timeDisplay}
            </div>
        `;
    }

    /**
     * 输入框变化处理
     */
    handleInputChange(e) {
        this.updateCharCounter();
        this.updateSendButton();
        this.autoResizeTextarea(e.target);
    }

    /**
     * 更新字符计数器
     */
    updateCharCounter() {
        if (this.elements.char_counter && this.elements.message_input) {
            const length = this.elements.message_input.value.length;
            this.elements.char_counter.textContent = `${length}/1000`;
        }
    }

    /**
     * 更新发送按钮状态
     */
    updateSendButton() {
        if (!this.elements.message_input || !this.elements.send_btn) {
            return;
        }
        
        const hasContent = this.elements.message_input.value.trim().length > 0;
        const canSend = hasContent && !this.state.isLoading && this.state.isConnected;
        
        this.elements.send_btn.disabled = !canSend;
    }

    /**
     * 自动调整文本域高度
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    /**
     * 设置加载状态
     */
    setLoading(isLoading) {
        this.state.isLoading = isLoading;
        this.updateSendButton();
        
        if (this.elements.loading_indicator) {
            this.elements.loading_indicator.classList.toggle('hidden', !isLoading);
        }
    }

    /**
     * 更新连接状态
     */
    updateConnectionStatus(isConnected = null) {
        if (isConnected !== null) {
            this.state.isConnected = isConnected;
        }

        if (this.elements.connection_status) {
            const statusText = this.state.isConnected ? '已连接' : '连接失败';
            const statusIcon = this.elements.connection_status.querySelector('i');
            const statusSpan = this.elements.connection_status.querySelector('span');
            
            // 安全检查span元素是否存在
            if (statusSpan) {
                statusSpan.textContent = statusText;
            } else {
                // 如果没有span，直接设置整个元素的文本（排除图标）
                const textNodes = Array.from(this.elements.connection_status.childNodes)
                    .filter(node => node.nodeType === Node.TEXT_NODE);
                if (textNodes.length > 0) {
                    textNodes[textNodes.length - 1].textContent = statusText;
                } else {
                    // 创建span元素
                    const span = document.createElement('span');
                    span.textContent = statusText;
                    this.elements.connection_status.appendChild(span);
                }
            }
            
            if (statusIcon) {
                statusIcon.style.color = this.state.isConnected ? 'var(--success-color)' : 'var(--error-color)';
            }
        }

        this.updateSendButton();
    }

    /**
     * 滚动到底部
     */
    scrollToBottom() {
        requestAnimationFrame(() => {
            this.elements.messages_container.scrollTop = this.elements.messages_container.scrollHeight;
        });
    }

    /**
     * 清空聊天记录
     */
    clearChat() {
        if (confirm('确定要清空所有聊天记录吗？')) {
            // 保留欢迎消息，删除其他消息
            const welcomeMessage = this.elements.messages_container.querySelector('.welcome-message');
            this.elements.messages_container.innerHTML = '';
            
            if (welcomeMessage) {
                this.elements.messages_container.appendChild(welcomeMessage);
            }
            
            this.state.messageCount = 0;
            this.showSuccess('聊天记录已清空');
        }
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const newTheme = this.state.currentTheme === 'light' ? 'dark' : 'light';
        this.state.currentTheme = newTheme;
        
        document.documentElement.setAttribute('data-theme', newTheme);
        
        const themeIcon = this.elements.toggle_theme.querySelector('i');
        if (themeIcon) {
            themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        this.saveSettings();
    }

    /**
     * 切换设置面板
     */
    toggleSettings() {
        if (this.elements.settings_panel) {
            this.elements.settings_panel.classList.toggle('hidden');
        }
    }

    /**
     * 关闭设置面板
     */
    closeSettings() {
        if (this.elements.settings_panel) {
            this.elements.settings_panel.classList.add('hidden');
        }
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        if (this.elements.error_toast && this.elements.error_message) {
            this.elements.error_message.textContent = message;
            this.elements.error_toast.classList.remove('hidden');
            
            // 5秒后自动隐藏
            setTimeout(() => this.hideError(), 5000);
        } else {
            // 如果Toast元素不存在，使用alert作为备选
            console.error('Error toast elements not found, using alert:', message);
            alert(`错误: ${message}`);
        }
    }

    /**
     * 隐藏错误消息
     */
    hideError() {
        if (this.elements.error_toast) {
            this.elements.error_toast.classList.add('hidden');
        }
    }

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        if (this.elements.success_toast && this.elements.success_message) {
            this.elements.success_message.textContent = message;
            this.elements.success_toast.classList.remove('hidden');
            
            // 3秒后自动隐藏
            setTimeout(() => {
                this.elements.success_toast.classList.add('hidden');
            }, 3000);
        } else {
            // 如果Toast元素不存在，使用console.log作为备选
            console.log('Success:', message);
        }
    }

    /**
     * 播放通知声音
     */
    playNotificationSound() {
        try {
            // 创建音频上下文播放提示音
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            gainNode.gain.value = 0.1;
            
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (error) {
            console.warn('播放提示音失败:', error);
        }
    }

    /**
     * 保存设置
     */
    saveSettings() {
        const settings = {
            sessionId: this.config.sessionId,
            autoScroll: this.elements.auto_scroll?.checked ?? true,
            showTimestamp: this.elements.show_timestamp?.checked ?? true,
            soundEnabled: this.elements.sound_enabled?.checked ?? false,
            theme: this.state.currentTheme
        };

        localStorage.setItem('polytool-chat-settings', JSON.stringify(settings));
    }

    /**
     * 加载设置
     */
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('polytool-chat-settings');
            if (savedSettings) {
                const settings = JSON.parse(savedSettings);
                
                // 应用设置
                this.config.sessionId = settings.sessionId || this.config.sessionId;
                this.config.autoScroll = settings.autoScroll ?? true;
                this.config.showTimestamp = settings.showTimestamp ?? true;
                this.config.soundEnabled = settings.soundEnabled ?? false;
                
                // 更新UI
                if (this.elements.session_id) {
                    this.elements.session_id.value = this.config.sessionId;
                }
                if (this.elements.auto_scroll) {
                    this.elements.auto_scroll.checked = this.config.autoScroll;
                }
                if (this.elements.show_timestamp) {
                    this.elements.show_timestamp.checked = this.config.showTimestamp;
                }
                if (this.elements.sound_enabled) {
                    this.elements.sound_enabled.checked = this.config.soundEnabled;
                }
                
                // 应用主题
                if (settings.theme) {
                    this.state.currentTheme = settings.theme;
                    document.documentElement.setAttribute('data-theme', settings.theme);
                    
                    const themeIcon = this.elements.toggle_theme?.querySelector('i');
                    if (themeIcon) {
                        themeIcon.className = settings.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
                    }
                }
            }
        } catch (error) {
            console.warn('加载设置失败:', error);
        }
    }

    /**
     * 生成会话ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * HTML转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 延迟函数
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.polytoolChat = new PolytoolChatClient();
});

// 导出类以供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PolytoolChatClient;
}