import os
import json
import requests
from openai import OpenAI
from typing import Dict, List, Optional, Any

class AIService:
    """AI服务管理类，支持多种AI模型"""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用的AI模型列表"""
        return [
            {
                'id': 'deepseek-r1',
                'name': 'DeepSeek R1',
                'description': '免费开源模型，编程能力强',
                'type': 'coding',
                'cost': 'free',
                'context_window': 128000
            },
            {
                'id': 'gemini-2.5-flash',
                'name': 'Gemini 2.5 Flash',
                'description': '大上下文窗口，混合推理',
                'type': 'reasoning',
                'cost': 'paid',
                'context_window': 1000000
            },
            {
                'id': 'claude-3.5-sonnet',
                'name': 'Claude 3.5 Sonnet',
                'description': '商业模型，编程能力强',
                'type': 'coding',
                'cost': 'paid',
                'context_window': 200000
            },
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'description': 'OpenAI小型模型，成本低',
                'type': 'general',
                'cost': 'paid',
                'context_window': 128000
            }
        ]
    
    def analyze_code(self, code: str, file_type: str, model: str = 'deepseek-r1') -> Dict[str, Any]:
        """分析代码质量和结构"""
        prompt = f"""
请分析以下{file_type}代码，提供详细的分析报告：

代码内容：
```{file_type}
{code}
```

请从以下方面进行分析：
1. 代码质量评估
2. 潜在问题和bug
3. 性能优化建议
4. 代码结构和设计模式
5. 安全性问题
6. 可维护性评估

请以JSON格式返回分析结果。
"""
        
        try:
            response = self._call_model(model, prompt)
            return {
                'success': True,
                'analysis': response,
                'model_used': model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_used': model
            }
    
    def generate_code(self, description: str, language: str, model: str = 'deepseek-r1') -> Dict[str, Any]:
        """根据描述生成代码"""
        prompt = f"""
请根据以下描述生成{language}代码：

需求描述：
{description}

要求：
1. 代码应该是完整的、可运行的
2. 包含必要的注释
3. 遵循最佳实践
4. 考虑错误处理
5. 代码风格规范

请只返回代码，不要包含其他解释。
"""
        
        try:
            response = self._call_model(model, prompt)
            return {
                'success': True,
                'code': response,
                'language': language,
                'model_used': model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_used': model
            }
    
    def modify_code(self, original_code: str, modification_request: str, file_type: str, model: str = 'deepseek-r1') -> Dict[str, Any]:
        """修改现有代码"""
        prompt = f"""
请根据以下要求修改{file_type}代码：

原始代码：
```{file_type}
{original_code}
```

修改要求：
{modification_request}

请返回修改后的完整代码，并说明做了哪些修改。
"""
        
        try:
            response = self._call_model(model, prompt)
            return {
                'success': True,
                'modified_code': response,
                'model_used': model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_used': model
            }
    
    def review_code(self, code: str, file_type: str, model: str = 'deepseek-r1') -> Dict[str, Any]:
        """代码审查"""
        prompt = f"""
请对以下{file_type}代码进行详细的代码审查：

代码内容：
```{file_type}
{code}
```

请从以下方面进行审查：
1. 代码规范性
2. 逻辑正确性
3. 性能问题
4. 安全漏洞
5. 可读性和可维护性
6. 测试覆盖建议

请提供具体的改进建议和修改方案。
"""
        
        try:
            response = self._call_model(model, prompt)
            return {
                'success': True,
                'review': response,
                'model_used': model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_used': model
            }
    
    def _call_model(self, model: str, prompt: str) -> str:
        """调用指定的AI模型"""
        if model == 'deepseek-r1':
            return self._call_deepseek(prompt)
        elif model.startswith('gemini'):
            return self._call_gemini(prompt, model)
        elif model.startswith('claude'):
            return self._call_claude(prompt, model)
        elif model.startswith('gpt'):
            return self._call_openai(prompt, model)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _call_deepseek(self, prompt: str) -> str:
        """调用DeepSeek模型"""
        # 由于DeepSeek R1是开源模型，这里使用OpenAI兼容的API
        # 实际部署时需要配置DeepSeek的API端点
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # 暂时使用GPT-4o-mini作为替代
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant with expertise in code analysis and generation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    def _call_gemini(self, prompt: str, model: str) -> str:
        """调用Gemini模型"""
        # 这里需要配置Gemini API
        # 暂时返回模拟响应
        return f"Gemini {model} response for: {prompt[:100]}..."
    
    def _call_claude(self, prompt: str, model: str) -> str:
        """调用Claude模型"""
        # 这里需要配置Claude API
        # 暂时返回模拟响应
        return f"Claude {model} response for: {prompt[:100]}..."
    
    def _call_openai(self, prompt: str, model: str) -> str:
        """调用OpenAI模型"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant with expertise in code analysis and generation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

# 全局AI服务实例
ai_service = AIService()

