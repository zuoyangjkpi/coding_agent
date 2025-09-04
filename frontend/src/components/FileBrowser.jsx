import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Folder, 
  File, 
  FolderOpen, 
  Search, 
  RefreshCw,
  Github,
  Download,
  GitBranch
} from 'lucide-react'
import axios from 'axios'

const FileBrowser = ({ project, onFileSelect, selectedFile }) => {
  const [fileTree, setFileTree] = useState(null)
  const [loading, setLoading] = useState(false)
  const [expandedFolders, setExpandedFolders] = useState(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [isCloning, setIsCloning] = useState(false)

  useEffect(() => {
    if (project && project.status === 'ready') {
      loadFileTree()
    }
  }, [project])

  const loadFileTree = async () => {
    if (!project) return
    
    setLoading(true)
    try {
      const response = await axios.get(`/api/github/file-tree/${project.id}`)
      if (response.data.success) {
        setFileTree(response.data.tree)
      }
    } catch (error) {
      console.error('Failed to load file tree:', error)
    } finally {
      setLoading(false)
    }
  }

  const cloneRepository = async () => {
    if (!project || !project.github_url) return
    
    setIsCloning(true)
    try {
      const response = await axios.post('/api/github/clone', {
        project_id: project.id,
        github_url: project.github_url
      })
      
      if (response.data.success) {
        // 重新加载项目状态
        window.location.reload()
      }
    } catch (error) {
      console.error('Failed to clone repository:', error)
    } finally {
      setIsCloning(false)
    }
  }

  const toggleFolder = (path) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedFolders(newExpanded)
  }

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    const iconMap = {
      'py': '🐍',
      'js': '📜',
      'ts': '📘',
      'jsx': '⚛️',
      'tsx': '⚛️',
      'java': '☕',
      'cpp': '⚙️',
      'c': '⚙️',
      'cs': '🔷',
      'php': '🐘',
      'rb': '💎',
      'go': '🐹',
      'rs': '🦀',
      'html': '🌐',
      'css': '🎨',
      'json': '📋',
      'md': '📝',
      'yml': '⚙️',
      'yaml': '⚙️'
    }
    return iconMap[ext] || '📄'
  }

  const renderFileTree = (items, parentPath = '') => {
    if (!items) return null

    return items
      .filter(item => 
        searchTerm === '' || 
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map((item) => {
        const fullPath = parentPath ? `${parentPath}/${item.name}` : item.name
        const isExpanded = expandedFolders.has(fullPath)
        const isSelected = selectedFile?.path === item.path

        if (item.type === 'directory') {
          return (
            <div key={fullPath} className="select-none">
              <div
                className="flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer rounded"
                onClick={() => toggleFolder(fullPath)}
              >
                {isExpanded ? (
                  <FolderOpen className="w-4 h-4 mr-2 text-blue-600" />
                ) : (
                  <Folder className="w-4 h-4 mr-2 text-blue-600" />
                )}
                <span className="text-sm font-medium">{item.name}</span>
              </div>
              {isExpanded && item.children && (
                <div className="ml-4 border-l border-gray-200 pl-2">
                  {renderFileTree(item.children, fullPath)}
                </div>
              )}
            </div>
          )
        } else {
          return (
            <div
              key={fullPath}
              className={`flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer rounded ${
                isSelected ? 'bg-blue-50 border-l-2 border-blue-500' : ''
              }`}
              onClick={() => onFileSelect(item)}
            >
              <File className="w-4 h-4 mr-2 text-gray-600" />
              <span className="text-sm mr-2">{getFileIcon(item.name)}</span>
              <span className="text-sm flex-1">{item.name}</span>
              {item.size && (
                <Badge variant="outline" className="text-xs">
                  {formatFileSize(item.size)}
                </Badge>
              )}
            </div>
          )
        }
      })
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  if (!project) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <Folder className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">请选择一个项目</p>
        </CardContent>
      </Card>
    )
  }

  if (project.status === 'created' && project.github_url) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Github className="w-5 h-5 mr-2" />
            克隆仓库
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-8">
          <p className="text-gray-600 mb-4">
            项目已创建，点击下方按钮克隆GitHub仓库
          </p>
          <Button 
            onClick={cloneRepository} 
            disabled={isCloning}
            className="bg-green-600 hover:bg-green-700"
          >
            {isCloning ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                克隆中...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                克隆仓库
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (project.status === 'cloning') {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <RefreshCw className="w-8 h-8 text-blue-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">正在克隆仓库...</p>
        </CardContent>
      </Card>
    )
  }

  if (project.status === 'error') {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <div className="text-red-600 mb-4">❌</div>
          <p className="text-gray-600 mb-4">项目状态异常</p>
          <Button variant="outline" onClick={loadFileTree}>
            <RefreshCw className="w-4 h-4 mr-2" />
            重试
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <Folder className="w-5 h-5 mr-2" />
            文件浏览器
          </div>
          <Button variant="outline" size="sm" onClick={loadFileTree} disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="搜索文件..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : fileTree ? (
          <div className="max-h-96 overflow-y-auto p-4">
            {renderFileTree(fileTree.items)}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            暂无文件
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FileBrowser

