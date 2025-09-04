import pytest
import os
from unittest.mock import Mock, patch
from src.services.ai_service import AIService

class TestAIService:
    """AI服务测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.ai_service = AIService()
    
    def test_get_available_models(self):
        """测试获取可用模型列表"""
        models = self.ai_service.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # 检查模型结构
        for model in models:
            assert 'id' in model
            assert 'name' in model
            assert 'description' in model
            assert 'type' in model
            assert 'cost' in model
    
    def test_analyze_code_success(self):
        """测试代码分析成功情况"""
        test_code = "def hello_world():\n    print('Hello, World!')"
        
        with patch.object(self.ai_service, '_call_model') as mock_call:
            mock_call.return_value = "This is a simple Python function that prints 'Hello, World!'"
            
            result = self.ai_service.analyze_code(test_code, 'python', 'deepseek-r1')
            
            assert result['success'] is True
            assert 'analysis' in result
            assert result['model_used'] == 'deepseek-r1'
    
    def test_analyze_code_failure(self):
        """测试代码分析失败情况"""
        test_code = "def hello_world():\n    print('Hello, World!')"
        
        with patch.object(self.ai_service, '_call_model') as mock_call:
            mock_call.side_effect = Exception("API Error")
            
            result = self.ai_service.analyze_code(test_code, 'python', 'deepseek-r1')
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_generate_code_success(self):
        """测试代码生成成功情况"""
        description = "Create a function that adds two numbers"
        
        with patch.object(self.ai_service, '_call_model') as mock_call:
            mock_call.return_value = "def add_numbers(a, b):\n    return a + b"
            
            result = self.ai_service.generate_code(description, 'python', 'deepseek-r1')
            
            assert result['success'] is True
            assert 'code' in result
            assert result['language'] == 'python'
    
    def test_modify_code_success(self):
        """测试代码修改成功情况"""
        original_code = "def add(a, b):\n    return a + b"
        modification = "Add input validation"
        
        with patch.object(self.ai_service, '_call_model') as mock_call:
            mock_call.return_value = "def add(a, b):\n    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n        raise ValueError('Inputs must be numbers')\n    return a + b"
            
            result = self.ai_service.modify_code(original_code, modification, 'python', 'deepseek-r1')
            
            assert result['success'] is True
            assert 'modified_code' in result
    
    def test_review_code_success(self):
        """测试代码审查成功情况"""
        test_code = "def divide(a, b):\n    return a / b"
        
        with patch.object(self.ai_service, '_call_model') as mock_call:
            mock_call.return_value = "This function lacks error handling for division by zero."
            
            result = self.ai_service.review_code(test_code, 'python', 'deepseek-r1')
            
            assert result['success'] is True
            assert 'review' in result
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_call_openai(self):
        """测试OpenAI API调用"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            ai_service = AIService()
            result = ai_service._call_openai("Test prompt", "gpt-4o-mini")
            
            assert result == "Test response"
    
    def test_call_model_unsupported(self):
        """测试不支持的模型"""
        with pytest.raises(ValueError, match="Unsupported model"):
            self.ai_service._call_model("unsupported-model", "test prompt")
    
    def test_deepseek_fallback_to_openai(self):
        """测试DeepSeek回退到OpenAI"""
        # 模拟没有DeepSeek API密钥的情况
        self.ai_service.deepseek_client = None
        
        with patch.object(self.ai_service.openai_client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Fallback response"
            mock_create.return_value = mock_response
            
            result = self.ai_service._call_deepseek("Test prompt")
            
            assert result == "Fallback response"
            mock_create.assert_called_once()
    
    def test_claude_api_not_configured(self):
        """测试Claude API未配置的情况"""
        self.ai_service.anthropic_client = None
        
        result = self.ai_service._call_claude("Test prompt", "claude-3.5-sonnet")
        
        assert "Claude API未配置" in result
    
    def test_gemini_api_not_configured(self):
        """测试Gemini API未配置的情况"""
        self.ai_service.google_api_key = None
        
        result = self.ai_service._call_gemini("Test prompt", "gemini-2.5-flash")
        
        assert "Gemini API未配置" in result

