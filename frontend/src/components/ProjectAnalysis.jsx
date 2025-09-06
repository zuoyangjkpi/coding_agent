import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BarChart3, 
  Shield, 
  Zap, 
  Building, 
  FileText, 
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import axios from 'axios'

const ProjectAnalysis = ({ project }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisType, setAnalysisType] = useState('overview')
  const [selectedModel, setSelectedModel] = useState('deepseek-r1')
  
  const analysisTypes = [
    { id: 'overview', name: '项目概览', icon: BarChart3, description: '整体架构和代码质量分析' },
    { id: 'security', name: '安全分析', icon: Shield, description: '安全漏洞和风险评估' },
    { id: 'performance', name: '性能分析', icon: Zap, description: '性能瓶颈和优化建议' },
    { id: 'architecture', name: '架构分析', icon: Building, description: '架构模式和设计分析' }
  ]
  
  const aiModels = [
    { id: 'deepseek-r1', name: 'DeepSeek R1', description: '免费编程模型' },
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', description: '大上下文模型' },
    { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: '商业编程模型' }
  ]

  const analyzeProject = async () => {
    if (!project) return
    
    setIsAnalyzing(true)
    try {
      const response = await axios.post('/api/ai/analyze-project', {
        project_id: project.id,
        analysis_type: analysisType,
        model: selectedModel
      })
      
      if (response.data.success) {
        setAnalysisResult(response.data)
      } else {
        console.error('Analysis failed:', response.data.error)
      }
    } catch (error) {
      console.error('Failed to analyze project:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const formatAnalysisText = (text) => {
    if (!text) return ''
    
    // 简单的格式化：将数字列表转换为更好的显示
    return text
      .split('\n')
      .map((line, index) => {
        if (line.match(/^\d+\./)) {
          return <div key={index} className="mb-2 font-medium">{line}</div>
        } else if (line.trim().startsWith('-')) {
          return <div key={index} className="ml-4 mb-1 text-gray-600">{line}</div>
        } else if (line.trim() === '') {
          return <div key={index} className="mb-2"></div>
        } else {
          return <div key={index} className="mb-1">{line}</div>
        }
      })
  }

  if (!project) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            项目分析
          </CardTitle>
          <CardDescription>
            请先选择一个项目进行分析
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            项目整体分析
          </CardTitle>
          <CardDescription>
            使用AI对整个项目进行深度分析，获取架构、安全、性能等方面的洞察
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 分析类型选择 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {analysisTypes.map((type) => {
              const Icon = type.icon
              return (
                <Card 
                  key={type.id}
                  className={`cursor-pointer transition-colors ${
                    analysisType === type.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'hover:border-gray-300'
                  }`}
                  onClick={() => setAnalysisType(type.id)}
                >
                  <CardContent className="p-4 text-center">
                    <Icon className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                    <h3 className="font-medium text-sm">{type.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* AI模型选择 */}
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium">AI模型:</label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {aiModels.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    <div>
                      <div className="font-medium">{model.name}</div>
                      <div className="text-xs text-gray-500">{model.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 分析按钮 */}
          <Button 
            onClick={analyzeProject} 
            disabled={isAnalyzing}
            className="w-full"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                分析中...
              </>
            ) : (
              <>
                <BarChart3 className="w-4 h-4 mr-2" />
                开始分析项目
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* 分析结果 */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
              分析结果
            </CardTitle>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <Badge variant="outline">
                {analysisTypes.find(t => t.id === analysisResult.analysis_type)?.name}
              </Badge>
              <Badge variant="outline">
                {aiModels.find(m => m.id === analysisResult.model_used)?.name}
              </Badge>
              <span>分析了 {analysisResult.files_analyzed} 个文件</span>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="analysis" className="w-full">
              <TabsList>
                <TabsTrigger value="analysis">AI分析</TabsTrigger>
                <TabsTrigger value="overview">项目概览</TabsTrigger>
              </TabsList>
              
              <TabsContent value="analysis" className="mt-4">
                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {formatAnalysisText(analysisResult.ai_analysis?.analysis)}
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="overview" className="mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">项目信息</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div><strong>名称:</strong> {analysisResult.project_overview?.name}</div>
                        <div><strong>描述:</strong> {analysisResult.project_overview?.description || '无描述'}</div>
                        <div><strong>总文件数:</strong> {analysisResult.project_overview?.total_files}</div>
                        <div><strong>GitHub:</strong> 
                          <a 
                            href={analysisResult.project_overview?.github_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline ml-1"
                          >
                            查看仓库
                          </a>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">语言分布</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(analysisResult.project_overview?.languages || {}).map(([lang, count]) => (
                          <div key={lang} className="flex justify-between items-center">
                            <span className="text-sm">{lang}</span>
                            <Badge variant="secondary">{count} 文件</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ProjectAnalysis

