import { useState, useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Play, 
  Save, 
  Download, 
  Upload, 
  Zap, 
  Eye, 
  RefreshCw,
  FileText,
  Bug,
  Lightbulb
} from 'lucide-react'
import axios from 'axios'

const CodeEditor = ({ project, selectedFile, onFileChange }) => {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [theme, setTheme] = useState('vs-dark')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [aiModels] = useState([
    { id: 'deepseek-r1', name: 'DeepSeek R1', description: '免费编程模型' },
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', description: '大上下文模型' },
    { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: '商业编程模型' }
  ])
  const [selectedModel, setSelectedModel] = useState('deepseek-r1')
  const editorRef = useRef(null)

  useEffect(() => {
    if (selectedFile) {
      loadFileContent()
    }
  }, [selectedFile])

  const loadFileContent = async () => {
    if (!selectedFile || !project) return
    
    try {
      const response = await axios.post('/api/github/file-content', {
        project_id: project.id,
        file_path: selectedFile.path
      })
      
      if (response.data.success) {
        setCode(response.data.content)
        // 根据文件扩展名设置语言
        const ext = selectedFile.path.split('.').pop().toLowerCase()
        const langMap = {
          'py': 'python',
          'js': 'javascript',
          'ts': 'typescript',
          'jsx': 'javascript',
          'tsx': 'typescript',
          'java': 'java',
          'cpp': 'cpp',
          'c': 'c',
          'cs': 'csharp',
          'php': 'php',
          'rb': 'ruby',
          'go': 'go',
          'rs': 'rust'
        }
        setLanguage(langMap[ext] || 'plaintext')
      }
    } catch (error) {
      console.error('Failed to load file content:', error)
    }
  }

  const saveFile = async () => {
    if (!selectedFile || !project) return
    
    try {
      const response = await axios.post('/api/github/save-file', {
        project_id: project.id,
        file_path: selectedFile.path,
        content: code
      })
      
      if (response.data.success) {
        // 触发文件更改回调
        if (onFileChange) {
          onFileChange(selectedFile.path, code)
        }
      }
    } catch (error) {
      console.error('Failed to save file:', error)
    }
  }

  const analyzeCode = async () => {
    if (!code.trim()) return
    
    setIsAnalyzing(true)
    try {
      const response = await axios.post('/api/ai/analyze-code', {
        code,
        file_type: language,
        model: selectedModel,
        project_id: project?.id
      })
      
      if (response.data.success) {
        setAnalysisResult(response.data)
      }
    } catch (error) {
      console.error('Failed to analyze code:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const reviewCode = async () => {
    if (!code.trim()) return
    
    setIsAnalyzing(true)
    try {
      const response = await axios.post('/api/ai/review-code', {
        code,
        file_type: language,
        model: selectedModel,
        project_id: project?.id
      })
      
      if (response.data.success) {
        setAnalysisResult({ ...response.data, type: 'review' })
      }
    } catch (error) {
      console.error('Failed to review code:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    
    // 设置编辑器选项
    editor.updateOptions({
      fontSize: 14,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true
    })
  }

  const renderAnalysisResult = () => {
    if (!analysisResult) return null

    const { ai_analysis, syntax_analysis, type } = analysisResult

    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="flex items-center">
            {type === 'review' ? (
              <>
                <Eye className="w-5 h-5 mr-2" />
                代码审查结果
              </>
            ) : (
              <>
                <Zap className="w-5 h-5 mr-2" />
                代码分析结果
              </>
            )}
            <Badge className="ml-2">{analysisResult.model_used}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="ai" className="w-full">
            <TabsList>
              <TabsTrigger value="ai">AI分析</TabsTrigger>
              {syntax_analysis && <TabsTrigger value="syntax">语法分析</TabsTrigger>}
            </TabsList>
            
            <TabsContent value="ai" className="space-y-4">
              {ai_analysis.success ? (
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-lg text-sm">
                    {type === 'review' ? ai_analysis.review : ai_analysis.analysis}
                  </pre>
                </div>
              ) : (
                <div className="text-red-600">
                  分析失败: {ai_analysis.error}
                </div>
              )}
            </TabsContent>
            
            {syntax_analysis && (
              <TabsContent value="syntax" className="space-y-4">
                {syntax_analysis.success ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">基础统计</h4>
                      <div className="space-y-1 text-sm">
                        <div>总行数: {syntax_analysis.basic_analysis?.total_lines}</div>
                        <div>代码行数: {syntax_analysis.basic_analysis?.code_lines}</div>
                        <div>注释行数: {syntax_analysis.basic_analysis?.comment_lines}</div>
                        <div>函数数量: {syntax_analysis.basic_analysis?.functions_count}</div>
                        <div>类数量: {syntax_analysis.basic_analysis?.classes_count}</div>
                      </div>
                    </div>
                    
                    {syntax_analysis.quality_analysis && (
                      <div>
                        <h4 className="font-medium mb-2">质量评分</h4>
                        <div className="space-y-1 text-sm">
                          <div>质量评分: {syntax_analysis.quality_analysis.quality_score}/100</div>
                          <div>问题总数: {syntax_analysis.quality_analysis.issues?.length || 0}</div>
                          {syntax_analysis.quality_analysis.issues_by_severity && (
                            <div className="space-y-1">
                              <div className="text-red-600">
                                错误: {syntax_analysis.quality_analysis.issues_by_severity.error}
                              </div>
                              <div className="text-yellow-600">
                                警告: {syntax_analysis.quality_analysis.issues_by_severity.warning}
                              </div>
                              <div className="text-blue-600">
                                信息: {syntax_analysis.quality_analysis.issues_by_severity.info}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-red-600">
                    语法分析失败: {syntax_analysis.error}
                  </div>
                )}
              </TabsContent>
            )}
          </Tabs>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* 工具栏 */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-white border rounded-lg">
        <div className="flex items-center space-x-4">
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
              <SelectItem value="typescript">TypeScript</SelectItem>
              <SelectItem value="java">Java</SelectItem>
              <SelectItem value="cpp">C++</SelectItem>
              <SelectItem value="c">C</SelectItem>
              <SelectItem value="csharp">C#</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={theme} onValueChange={setTheme}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="vs-dark">深色主题</SelectItem>
              <SelectItem value="light">浅色主题</SelectItem>
              <SelectItem value="hc-black">高对比度</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {aiModels.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={saveFile} disabled={!selectedFile}>
            <Save className="w-4 h-4 mr-2" />
            保存
          </Button>
          <Button variant="outline" size="sm" onClick={analyzeCode} disabled={isAnalyzing || !code.trim()}>
            {isAnalyzing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            分析代码
          </Button>
          <Button variant="outline" size="sm" onClick={reviewCode} disabled={isAnalyzing || !code.trim()}>
            {isAnalyzing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Eye className="w-4 h-4 mr-2" />
            )}
            代码审查
          </Button>
        </div>
      </div>

      {/* 编辑器 */}
      <div className="border rounded-lg overflow-hidden">
        <Editor
          height="500px"
          language={language}
          theme={theme}
          value={code}
          onChange={setCode}
          onMount={handleEditorDidMount}
          options={{
            selectOnLineNumbers: true,
            roundedSelection: false,
            readOnly: false,
            cursorStyle: 'line',
            automaticLayout: true,
          }}
        />
      </div>

      {/* 分析结果 */}
      {renderAnalysisResult()}
    </div>
  )
}

export default CodeEditor

