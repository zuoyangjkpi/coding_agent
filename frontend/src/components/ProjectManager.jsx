import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Plus, Github, Folder, Clock, AlertCircle } from 'lucide-react'
import axios from 'axios'

const ProjectManager = ({ onProjectSelect }) => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    github_url: ''
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects')
      if (response.data.success) {
        setProjects(response.data.projects)
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const createProject = async () => {
    try {
      const response = await axios.post('/api/projects', newProject)
      if (response.data.success) {
        setProjects([...projects, response.data.project])
        setNewProject({ name: '', description: '', github_url: '' })
        setIsCreateDialogOpen(false)
      }
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      created: { color: 'bg-gray-500', text: '已创建' },
      cloning: { color: 'bg-blue-500', text: '克隆中' },
      analyzing: { color: 'bg-yellow-500', text: '分析中' },
      ready: { color: 'bg-green-500', text: '就绪' },
      error: { color: 'bg-red-500', text: '错误' }
    }
    
    const config = statusConfig[status] || statusConfig.created
    return (
      <Badge className={`${config.color} text-white`}>
        {config.text}
      </Badge>
    )
  }

  const handleDelete = async (projectId, e) => {
    // 阻止事件冒泡，避免触发项目选择
    if (e && e.stopPropagation) {
      e.stopPropagation();
    }
    
    // 添加确认对话框
    if (!window.confirm('确定要删除这个项目吗？此操作不可撤销。')) {
      return;
    }
    
    try {
      console.log('尝试删除项目', projectId);
      console.log('删除前项目列表:', projects.map(p => ({ id: p.id, name: p.name })));
      
      const response = await axios.delete(`/api/projects/${projectId}`);
      console.log('删除响应:', response.data);
      
      if (response.data.success) {
        // 更新本地状态，移除被删除的项目
        setProjects((prevProjects) => {
          const newProjects = prevProjects.filter((p) => p.id !== projectId);
          console.log('删除后项目列表:', newProjects.map(p => ({ id: p.id, name: p.name })));
          return newProjects;
        });
        
        console.log('删除成功', projectId);
        
        // 显示成功消息
        alert('项目删除成功！');
        
        // 强制重新获取项目列表以确保同步
        setTimeout(() => {
          fetchProjects();
        }, 100);
        
      } else {
        console.error('删除失败:', response.data.error);
        alert('删除失败: ' + response.data.error);
      }
    } catch (error) {
      console.error('删除项目失败:', error);
      
      // 更详细的错误处理
      if (error.response) {
        // 服务器返回了错误响应
        const errorMessage = error.response.data?.error || '服务器错误';
        console.error('服务器错误响应:', error.response.data);
        alert('删除失败: ' + errorMessage);
      } else if (error.request) {
        // 请求发送了但没有收到响应
        console.error('网络请求失败:', error.request);
        alert('删除失败: 无法连接到服务器，请检查网络连接');
      } else {
        // 其他错误
        console.error('其他错误:', error.message);
        alert('删除失败: ' + error.message);
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">项目管理</h2>
          <p className="text-gray-600">管理您的代码项目和AI分析任务</p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              新建项目
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>创建新项目</DialogTitle>
              <DialogDescription>
                创建一个新的代码分析项目。您可以稍后添加GitHub仓库。
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">项目名称</Label>
                <Input
                  id="name"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="输入项目名称"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">项目描述</Label>
                <Textarea
                  id="description"
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="输入项目描述（可选）"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="github_url">GitHub URL</Label>
                <Input
                  id="github_url"
                  value={newProject.github_url}
                  onChange={(e) => setNewProject({ ...newProject, github_url: e.target.value })}
                  placeholder="https://github.com/user/repo（可选）"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={createProject} disabled={!newProject.name}>
                创建项目
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {projects.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Folder className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无项目</h3>
            <p className="text-gray-600 mb-4">创建您的第一个项目开始使用AI代码分析</p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              创建项目
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
          <Card
            key={project.id}
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => onProjectSelect(project)}
          >
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{project.name}</CardTitle>
                {getStatusBadge(project.status)}
              </div>
              <CardDescription className="line-clamp-2">
                {project.description || '暂无描述'}
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-2">
                {project.github_url && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Github className="w-4 h-4 mr-2" />
                    <span className="truncate">{project.github_url}</span>
                  </div>
                )}
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>创建于 {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                {project.status === 'error' && (
                  <div className="flex items-center text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    <span>项目状态异常</span>
                  </div>
                )}
              </div>
            </CardContent>
            <div className="flex justify-end px-4 pb-4">
              <Button
                variant="destructive"
                onClick={(e) => handleDelete(project.id, e)}
              >
                删除
              </Button>
            </div>
          </Card>
        ))}
        </div>
      )}
    </div>
  )
}

export default ProjectManager

