import os
import json
import requests
from openai import OpenAI
import anthropic
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIService:
    """AI服务管理类，支持多种AI模型"""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        
        # 初始化Anthropic客户端
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.anthropic_client = None
            
        # 初始化Google AI客户端
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        
        # 初始化DeepSeek客户端
        if self.deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url
            )
        else:
            self.deepseek_client = None
        
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
        try:
            if self.deepseek_client:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-r1",
                    messages=[
                        {"role": "system", "content": "You are a helpful coding assistant with expertise in code analysis and generation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            else:
                # 如果没有DeepSeek API密钥，使用OpenAI作为备选
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
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
        """调用Gemini模型 (Google AI API)"""
        try:
            if not self.google_api_key:
                return f"Gemini API未配置，请设置GOOGLE_API_KEY环境变量"
            
            # 根据模型名称选择对应的Gemini模型
            model_name = "gemini-2.0-flash-exp" if "2.5" in model else "gemini-1.5-flash"
            
            model_instance = genai.GenerativeModel(model_name)
            response = model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.1,
                )
            )
            return response.text
        except Exception as e:
            return f"Gemini API error: {str(e)}"
    
    def _call_claude(self, prompt: str, model: str) -> str:
        """调用Claude模型 (Anthropic API)"""
        try:
            if not self.anthropic_client:
                return f"Claude API未配置，请设置ANTHROPIC_API_KEY环境变量"
            
            # 根据模型名称选择对应的Claude模型
            claude_model = "claude-3-5-sonnet-20241022" if "3.5" in model else "claude-3-haiku-20240307"
            
            response = self.anthropic_client.messages.create(
                model=claude_model,
                max_tokens=4000,
                temperature=0.1,
                system="You are a helpful coding assistant with expertise in code analysis and generation.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Claude API error: {str(e)}"
    
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


    def analyze_project(self, project_overview: dict, important_files: list, analysis_type: str = 'overview', model: str = 'deepseek-r1') -> dict:
        """分析整个项目"""
        try:
            # 构建分析提示
            if analysis_type == 'overview':
                prompt = f"""
请分析以下项目的整体结构和代码质量：

项目信息：
- 名称：{project_overview.get('name', 'Unknown')}
- 描述：{project_overview.get('description', 'No description')}
- 总文件数：{project_overview.get('total_files', 0)}
- 语言分布：{project_overview.get('languages', {})}

主要文件内容：
"""
                for file in important_files:
                    prompt += f"\n文件：{file['path']} ({file['type']})\n```\n{file['content']}\n```\n"
                
                prompt += """
请提供以下分析：
1. 项目架构概览
2. 代码质量评估
3. 技术栈分析
4. 潜在问题和改进建议
5. 项目复杂度评估

请用中文回答，格式清晰。
"""
            
            elif analysis_type == 'security':
                prompt = f"""
请对以下项目进行安全性分析：

项目信息：
- 名称：{project_overview.get('name', 'Unknown')}
- 语言分布：{project_overview.get('languages', {})}

主要文件内容：
"""
                for file in important_files:
                    prompt += f"\n文件：{file['path']} ({file['type']})\n```\n{file['content']}\n```\n"
                
                prompt += """
请重点分析：
1. 安全漏洞检测
2. 敏感信息泄露风险
3. 输入验证问题
4. 权限控制缺陷
5. 安全最佳实践建议

请用中文回答，重点标注高风险问题。
"""
            
            elif analysis_type == 'performance':
                prompt = f"""
请对以下项目进行性能分析：

项目信息：
- 名称：{project_overview.get('name', 'Unknown')}
- 语言分布：{project_overview.get('languages', {})}

主要文件内容：
"""
                for file in important_files:
                    prompt += f"\n文件：{file['path']} ({file['type']})\n```\n{file['content']}\n```\n"
                
                prompt += """
请重点分析：
1. 性能瓶颈识别
2. 算法复杂度分析
3. 内存使用优化
4. 数据库查询优化
5. 性能改进建议

请用中文回答，提供具体的优化方案。
"""
            
            elif analysis_type == 'architecture':
                prompt = f"""
请对以下项目进行架构分析：

项目信息：
- 名称：{project_overview.get('name', 'Unknown')}
- 文件结构：{[f['path'] for f in project_overview.get('file_structure', [])]}
- 语言分布：{project_overview.get('languages', {})}

主要文件内容：
"""
                for file in important_files:
                    prompt += f"\n文件：{file['path']} ({file['type']})\n```\n{file['content']}\n```\n"
                
                prompt += """
请重点分析：
1. 项目架构模式
2. 模块化程度
3. 依赖关系分析
4. 设计模式使用
5. 架构改进建议

请用中文回答，提供架构图建议。
"""
            
            else:
                prompt = f"请分析项目：{project_overview.get('name', 'Unknown')}"
            
            # 调用AI模型
            response = self._call_model(model, prompt)
            
            return {
                'success': True,
                'analysis': response,
                'analysis_type': analysis_type,
                'model_used': model,
                'files_analyzed': len(important_files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': analysis_type,
                'model_used': model
            }

