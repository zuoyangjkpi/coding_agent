import os
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from typing import Dict, List, Optional, Any
import json
import re

class CodeAnalysisService:
    """代码分析服务类，使用Tree-sitter进行代码解析"""
    
    def __init__(self):
        # 初始化支持的语言解析器
        self.parsers = {}
        self.languages = {}
        
        # 初始化Python解析器
        try:
            PY_LANGUAGE = Language(tspython.language())
            self.languages['python'] = PY_LANGUAGE
            
            parser = Parser(PY_LANGUAGE)
            self.parsers['python'] = parser
        except Exception as e:
            print(f"Failed to initialize Python parser: {e}")
    
    def analyze_file(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # 检测文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            language = self._detect_language(file_ext)
            
            if not language:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}'
                }
            
            # 基础分析
            basic_analysis = self._basic_analysis(content, language)
            
            # 语法分析（如果支持Tree-sitter）
            syntax_analysis = {}
            if language in self.parsers:
                syntax_analysis = self._syntax_analysis(content, language)
            
            # 代码质量分析
            quality_analysis = self._quality_analysis(content, language)
            
            return {
                'success': True,
                'file_path': file_path,
                'language': language,
                'basic_analysis': basic_analysis,
                'syntax_analysis': syntax_analysis,
                'quality_analysis': quality_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """分析整个项目"""
        try:
            analysis_results = []
            project_stats = {
                'total_files': 0,
                'total_lines': 0,
                'languages': {},
                'file_types': {},
                'complexity_score': 0,
                'issues_count': 0
            }
            
            # 遍历项目文件
            for root, dirs, files in os.walk(project_path):
                # 跳过常见的忽略目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    
                    # 只分析代码文件
                    if self._is_code_file(file):
                        try:
                            analysis = self.analyze_file(file_path)
                            if analysis['success']:
                                analysis_results.append({
                                    'file_path': relative_path,
                                    'analysis': analysis
                                })
                                
                                # 更新项目统计
                                self._update_project_stats(project_stats, analysis)
                                
                        except Exception as e:
                            print(f"Failed to analyze {relative_path}: {e}")
                            continue
            
            # 计算项目整体评分
            project_score = self._calculate_project_score(project_stats, analysis_results)
            
            return {
                'success': True,
                'project_path': project_path,
                'stats': project_stats,
                'score': project_score,
                'files_analyzed': len(analysis_results),
                'file_analyses': analysis_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _basic_analysis(self, content: str, language: str) -> Dict[str, Any]:
        """基础代码分析"""
        lines = content.split('\n')
        
        analysis = {
            'total_lines': len(lines),
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'max_line_length': 0,
            'avg_line_length': 0,
            'functions_count': 0,
            'classes_count': 0
        }
        
        total_length = 0
        
        for line in lines:
            stripped = line.strip()
            line_length = len(line)
            total_length += line_length
            
            if line_length > analysis['max_line_length']:
                analysis['max_line_length'] = line_length
            
            if not stripped:
                analysis['blank_lines'] += 1
            elif self._is_comment_line(stripped, language):
                analysis['comment_lines'] += 1
            else:
                analysis['code_lines'] += 1
        
        if lines:
            analysis['avg_line_length'] = total_length / len(lines)
        
        # 简单的函数和类计数
        if language == 'python':
            analysis['functions_count'] = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
            analysis['classes_count'] = len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
        elif language in ['javascript', 'typescript']:
            analysis['functions_count'] = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*:\s*function', content))
            analysis['classes_count'] = len(re.findall(r'class\s+\w+', content))
        
        return analysis
    
    def _syntax_analysis(self, content: str, language: str) -> Dict[str, Any]:
        """语法分析（使用Tree-sitter）"""
        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            
            analysis = {
                'parse_errors': [],
                'functions': [],
                'classes': [],
                'imports': [],
                'variables': [],
                'complexity_metrics': {}
            }
            
            # 遍历语法树
            self._traverse_tree(tree.root_node, analysis, content)
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _quality_analysis(self, content: str, language: str) -> Dict[str, Any]:
        """代码质量分析"""
        issues = []
        
        lines = content.split('\n')
        
        # 检查常见问题
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 行长度检查
            if len(line) > 120:
                issues.append({
                    'type': 'line_length',
                    'severity': 'warning',
                    'line': i,
                    'message': f'Line too long ({len(line)} characters)'
                })
            
            # 尾随空格检查
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    'type': 'trailing_whitespace',
                    'severity': 'info',
                    'line': i,
                    'message': 'Trailing whitespace'
                })
            
            # 语言特定检查
            if language == 'python':
                issues.extend(self._python_quality_checks(stripped, i))
            elif language in ['javascript', 'typescript']:
                issues.extend(self._javascript_quality_checks(stripped, i))
        
        # 计算质量评分
        quality_score = max(0, 100 - len(issues) * 2)
        
        return {
            'issues': issues,
            'quality_score': quality_score,
            'issues_by_severity': {
                'error': len([i for i in issues if i['severity'] == 'error']),
                'warning': len([i for i in issues if i['severity'] == 'warning']),
                'info': len([i for i in issues if i['severity'] == 'info'])
            }
        }
    
    def _python_quality_checks(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Python特定的质量检查"""
        issues = []
        
        # 检查import语句
        if line.startswith('from ') and ' import *' in line:
            issues.append({
                'type': 'wildcard_import',
                'severity': 'warning',
                'line': line_num,
                'message': 'Avoid wildcard imports'
            })
        
        # 检查print语句（可能是调试代码）
        if 'print(' in line and not line.strip().startswith('#'):
            issues.append({
                'type': 'debug_print',
                'severity': 'info',
                'line': line_num,
                'message': 'Consider removing debug print statement'
            })
        
        # 检查TODO注释
        if 'TODO' in line.upper() or 'FIXME' in line.upper():
            issues.append({
                'type': 'todo_comment',
                'severity': 'info',
                'line': line_num,
                'message': 'TODO/FIXME comment found'
            })
        
        return issues
    
    def _javascript_quality_checks(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """JavaScript/TypeScript特定的质量检查"""
        issues = []
        
        # 检查console.log
        if 'console.log(' in line:
            issues.append({
                'type': 'debug_console',
                'severity': 'info',
                'line': line_num,
                'message': 'Consider removing debug console.log'
            })
        
        # 检查var声明
        if re.match(r'^\s*var\s+', line):
            issues.append({
                'type': 'var_declaration',
                'severity': 'warning',
                'line': line_num,
                'message': 'Consider using let or const instead of var'
            })
        
        return issues
    
    def _traverse_tree(self, node, analysis: Dict[str, Any], content: str):
        """遍历语法树节点"""
        if node.type == 'function_definition':
            func_name = self._get_node_text(node, content)
            analysis['functions'].append({
                'name': func_name,
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1
            })
        elif node.type == 'class_definition':
            class_name = self._get_node_text(node, content)
            analysis['classes'].append({
                'name': class_name,
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1
            })
        
        # 递归遍历子节点
        for child in node.children:
            self._traverse_tree(child, analysis, content)
    
    def _get_node_text(self, node, content: str) -> str:
        """获取节点对应的文本"""
        try:
            start_byte = node.start_byte
            end_byte = node.end_byte
            return content[start_byte:end_byte]
        except:
            return "unknown"
    
    def _detect_language(self, file_ext: str) -> Optional[str]:
        """检测编程语言"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript'
        }
        return language_map.get(file_ext)
    
    def _is_code_file(self, filename: str) -> bool:
        """判断是否为代码文件"""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.html',
            '.css', '.scss', '.less', '.sql', '.sh', '.bash'
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in code_extensions
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """判断是否为注释行"""
        if language == 'python':
            return line.startswith('#')
        elif language in ['javascript', 'typescript', 'java', 'cpp', 'c', 'cs']:
            return line.startswith('//') or line.startswith('/*') or line.startswith('*')
        elif language == 'html':
            return line.startswith('<!--')
        elif language == 'css':
            return line.startswith('/*')
        return False
    
    def _update_project_stats(self, stats: Dict[str, Any], analysis: Dict[str, Any]):
        """更新项目统计信息"""
        if analysis['success']:
            stats['total_files'] += 1
            
            basic = analysis.get('basic_analysis', {})
            stats['total_lines'] += basic.get('total_lines', 0)
            
            language = analysis.get('language', 'unknown')
            stats['languages'][language] = stats['languages'].get(language, 0) + 1
            
            quality = analysis.get('quality_analysis', {})
            stats['issues_count'] += len(quality.get('issues', []))
    
    def _calculate_project_score(self, stats: Dict[str, Any], analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算项目整体评分"""
        if not analyses:
            return {'overall_score': 0, 'details': 'No files analyzed'}
        
        total_quality_score = 0
        total_files = len(analyses)
        
        for analysis_result in analyses:
            analysis = analysis_result.get('analysis', {})
            quality = analysis.get('quality_analysis', {})
            total_quality_score += quality.get('quality_score', 0)
        
        overall_score = total_quality_score / total_files if total_files > 0 else 0
        
        return {
            'overall_score': round(overall_score, 2),
            'total_files_analyzed': total_files,
            'average_quality_score': round(overall_score, 2),
            'total_issues': stats['issues_count'],
            'details': f'Analyzed {total_files} files with {stats["issues_count"]} total issues'
        }

# 全局代码分析服务实例
code_analysis_service = CodeAnalysisService()

