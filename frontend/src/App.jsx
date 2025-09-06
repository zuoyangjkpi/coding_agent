import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Wifi, WifiOff, Folder, Code, BarChart3, Brain, Home, Github, FileText } from 'lucide-react'
import ProjectManager from './components/ProjectManager'
import FileBrowser from './components/FileBrowser'
import CodeEditor from './components/CodeEditor'
import ProjectAnalysis from './components/ProjectAnalysis'
import io from 'socket.io-client'
import axios from 'axios'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('projects')
  const [selectedProject, setSelectedProject] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [socket, setSocket] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')

  useEffect(() => {
    // 在开发环境中，直接连接到后端，不使用代理
    const isDevelopment = import.meta.env.DEV;
    const backendURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';
    
    console.log('Environment:', isDevelopment ? 'development' : 'production');
    console.log('Backend URL:', backendURL);

    // 设置axios默认配置
    if (isDevelopment) {
      // 开发环境使用代理，所以baseURL设为空
      axios.defaults.baseURL = '';
    } else {
      // 生产环境直接指向后端
      axios.defaults.baseURL = backendURL;
    }

    // 初始化Socket.IO连接 - 直接连接到后端，不通过代理
    const socketInstance = io(backendURL, {
      path: '/socket.io',
      transports: ['polling', 'websocket'], // 优先使用polling避免WebSocket代理问题
      timeout: 10000,
      forceNew: true,
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });
    setSocket(socketInstance);

    socketInstance.on('connect', () => {
      setConnectionStatus('connected')
      console.log('Connected to server:', socketInstance.id)
    })

    socketInstance.on('disconnect', (reason) => {
      setConnectionStatus('disconnected')
      console.log('Disconnected from server:', reason)
    })

    socketInstance.on('connect_error', (error) => {
      setConnectionStatus('disconnected')
      console.error('Connection error:', error)
    })

    socketInstance.on('analysis_update', (data) => {
      console.log('Analysis update:', data)
      // 这里可以处理实时分析更新
    })

    return () => {
      socketInstance.disconnect()
    }
  }, [])

  useEffect(() => {
    if (socket && selectedProject) {
      socket.emit('join_project', { project_id: selectedProject.id })
      return () => {
        socket.emit('leave_project', { project_id: selectedProject.id })
      }
    }
  }, [socket, selectedProject])

  const handleProjectSelect = (project) => {
    setSelectedProject(project)
    setSelectedFile(null)
    setCurrentView('workspace')
  }

  const handleFileSelect = (file) => {
    setSelectedFile(file)
  }

  const handleFileChange = (filePath, content) => {
    // 处理文件内容更改
    console.log('File changed:', filePath, content.length)
  }

  const renderHeader = () => (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Coding Agent</h1>
          </div>
          <Badge variant={connectionStatus === 'connected' ? 'default' : 'destructive'}>
            {connectionStatus === 'connected' ? '已连接' : '未连接'}
          </Badge>
        </div>
        
        <nav className="flex items-center space-x-4">
          <Button
            variant={currentView === 'projects' ? 'default' : 'ghost'}
            onClick={() => setCurrentView('projects')}
          >
            <Home className="w-4 h-4 mr-2" />
            项目
          </Button>
          {selectedProject && (
            <Button
              variant={currentView === 'workspace' ? 'default' : 'ghost'}
              onClick={() => setCurrentView('workspace')}
            >
              <Code className="w-4 h-4 mr-2" />
              工作区
            </Button>
          )}
        </nav>
      </div>
    </header>
  )

  const renderProjectsView = () => (
    <div className="p-6">
      <ProjectManager onProjectSelect={handleProjectSelect} />
    </div>
  )

  const renderWorkspaceView = () => {
    if (!selectedProject) {
      return (
        <div className="flex items-center justify-center h-full">
          <Card className="text-center">
            <CardContent className="py-12">
              <Folder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">未选择项目</h3>
              <p className="text-gray-600 mb-4">请先选择一个项目开始工作</p>
              <Button onClick={() => setCurrentView('projects')}>
                选择项目
              </Button>
            </CardContent>
          </Card>
        </div>
      )
    }

    return (
      <div className="flex h-full">
        {/* 侧边栏 - 文件浏览器和项目分析 */}
        <div className="w-80 border-r border-gray-200 bg-gray-50">
          <div className="p-4 border-b border-gray-200 bg-white">
            <h2 className="font-semibold text-gray-900">{selectedProject.name}</h2>
            <p className="text-sm text-gray-600 truncate">
              {selectedProject.description || '暂无描述'}
            </p>
            {selectedProject.github_url && (
              <div className="flex items-center mt-2 text-sm text-gray-600">
                <Github className="w-4 h-4 mr-1" />
                <span className="truncate">{selectedProject.github_url}</span>
              </div>
            )}
          </div>
          <Tabs defaultValue="files" className="h-full">
            <TabsList className="grid w-full grid-cols-2 mx-4 mt-2">
              <TabsTrigger value="files" className="text-xs">
                <Folder className="w-3 h-3 mr-1" />
                文件
              </TabsTrigger>
              <TabsTrigger value="analysis" className="text-xs">
                <BarChart3 className="w-3 h-3 mr-1" />
                分析
              </TabsTrigger>
            </TabsList>
            <TabsContent value="files" className="p-4 h-full">
              <FileBrowser
                project={selectedProject}
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
              />
            </TabsContent>
            <TabsContent value="analysis" className="p-4 h-full overflow-y-auto">
              <ProjectAnalysis project={selectedProject} />
            </TabsContent>
          </Tabs>
        </div>

        {/* 主内容区 */}
        <div className="flex-1 flex flex-col">
          {selectedFile ? (
            <div className="flex-1 p-6">
              <div className="mb-4">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-gray-600" />
                  <span className="font-medium">{selectedFile.name}</span>
                  <Badge variant="outline">{selectedFile.path}</Badge>
                </div>
              </div>
              <CodeEditor
                project={selectedProject}
                selectedFile={selectedFile}
                onFileChange={handleFileChange}
              />
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <Card className="text-center">
                <CardContent className="py-12">
                  <Code className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">未选择文件</h3>
                  <p className="text-gray-600">从左侧文件浏览器中选择一个文件开始编辑</p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {renderHeader()}
      
      <main className="flex-1 overflow-hidden">
        {currentView === 'projects' && renderProjectsView()}
        {currentView === 'workspace' && renderWorkspaceView()}
      </main>
    </div>
  )
}

export default App
