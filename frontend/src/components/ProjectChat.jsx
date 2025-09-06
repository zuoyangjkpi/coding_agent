import React, { useState, useRef, useEffect } from 'react';
import { Button, Input, Card, Avatar, Spin, Select, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, SettingOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const ProjectChat = ({ project, visible, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const messagesEndRef = useRef(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 获取可用模型
  useEffect(() => {
    if (visible) {
      fetchAvailableModels();
      // 添加欢迎消息
      if (messages.length === 0) {
        setMessages([{
          id: Date.now(),
          role: 'assistant',
          content: `你好！我是你的编程助手。我已经了解了项目 "${project?.name}" 的代码结构，可以帮你：\n\n• 分析和解释代码\n• 提供编程建议\n• 帮助调试问题\n• 建议代码改进\n• 回答架构问题\n\n有什么我可以帮助你的吗？`,
          timestamp: new Date().toISOString(),
          model: 'system'
        }]);
      }
    }
  }, [visible, project]);

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chat/models`);
      const data = await response.json();
      if (data.success) {
        setAvailableModels(data.models);
        // 设置默认模型
        if (data.models.length > 0) {
          const defaultModel = data.models.find(m => m.primary_use === 'coding') || data.models[0];
          setSelectedModel(defaultModel.id);
        }
      }
    } catch (error) {
      console.error('获取模型列表失败:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chat/project/${project.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          model: selectedModel,
          history: messages.slice(-10) // 只发送最近10条消息作为上下文
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp,
          model: data.model_used
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        message.error(`聊天失败: ${data.error}`);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // 简单的markdown格式化
    return content
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-4/5 h-4/5 flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <RobotOutlined className="text-2xl text-blue-500" />
            <div>
              <h3 className="text-lg font-semibold">项目助手</h3>
              <p className="text-sm text-gray-500">{project?.name}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Select
              value={selectedModel}
              onChange={setSelectedModel}
              style={{ width: 200 }}
              size="small"
              placeholder="选择AI模型"
            >
              {availableModels.map(model => (
                <Option key={model.id} value={model.id}>
                  <div className="flex items-center justify-between">
                    <span>{model.name}</span>
                    <span className="text-xs text-gray-400">{model.type}</span>
                  </div>
                </Option>
              ))}
            </Select>
            <Button onClick={onClose}>关闭</Button>
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-3/4 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <Avatar
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  className={msg.role === 'user' ? 'bg-blue-500' : 'bg-green-500'}
                />
                <Card
                  className={`${msg.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'}`}
                  bodyStyle={{ padding: '12px' }}
                >
                  <div
                    className="text-sm"
                    dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                  />
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                    <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                    {msg.model && msg.model !== 'system' && (
                      <span className="bg-gray-200 px-2 py-1 rounded">{msg.model}</span>
                    )}
                  </div>
                </Card>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-2">
                <Avatar icon={<RobotOutlined />} className="bg-green-500" />
                <Card className="bg-gray-50" bodyStyle={{ padding: '12px' }}>
                  <Spin size="small" />
                  <span className="ml-2 text-sm text-gray-500">正在思考...</span>
                </Card>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <TextArea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入你的问题... (Shift+Enter 换行，Enter 发送)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              loading={loading}
              disabled={!inputMessage.trim()}
            >
              发送
            </Button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            提示：你可以询问关于代码的任何问题，我会基于项目的代码结构来回答
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectChat;

