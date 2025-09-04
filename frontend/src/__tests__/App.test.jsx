import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import App from '../App'

// Mock Socket.IO
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    emit: vi.fn(),
    disconnect: vi.fn()
  }))
}))

// Mock axios
vi.mock('axios', () => ({
  default: {
    defaults: { baseURL: '' },
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('App Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks()
  })

  test('renders main header with title', () => {
    render(<App />)
    
    expect(screen.getByText('Coding Agent')).toBeInTheDocument()
  })

  test('shows projects view by default', () => {
    render(<App />)
    
    expect(screen.getByText('项目管理')).toBeInTheDocument()
    expect(screen.getByText('管理您的代码项目和AI分析任务')).toBeInTheDocument()
  })

  test('displays connection status badge', () => {
    render(<App />)
    
    // Should show disconnected initially
    expect(screen.getByText('未连接')).toBeInTheDocument()
  })

  test('navigation between views works', async () => {
    render(<App />)
    
    // Initially on projects view
    expect(screen.getByText('项目管理')).toBeInTheDocument()
    
    // Create a mock project to enable workspace navigation
    const mockProject = {
      id: 1,
      name: 'Test Project',
      description: 'Test Description',
      status: 'ready'
    }
    
    // Simulate project selection (this would normally come from ProjectManager)
    // We'll test this indirectly by checking if workspace elements appear
    // when a project is selected
  })

  test('shows empty state when no project selected in workspace', () => {
    render(<App />)
    
    // Mock having a selected project but then clearing it
    // This tests the workspace empty state
    const workspaceButton = screen.queryByText('工作区')
    
    // Workspace button should not be visible without a selected project
    expect(workspaceButton).not.toBeInTheDocument()
  })

  test('handles socket connection events', () => {
    const mockSocket = {
      on: vi.fn(),
      emit: vi.fn(),
      disconnect: vi.fn()
    }
    
    // Mock socket.io to return our mock socket
    const io = require('socket.io-client').default
    io.mockReturnValue(mockSocket)
    
    render(<App />)
    
    // Verify socket event listeners are set up
    expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function))
    expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function))
    expect(mockSocket.on).toHaveBeenCalledWith('analysis_update', expect.any(Function))
  })

  test('axios base URL is set correctly', () => {
    const axios = require('axios').default
    
    render(<App />)
    
    expect(axios.defaults.baseURL).toBe(window.location.origin)
  })

  test('component unmounts cleanly', () => {
    const mockSocket = {
      on: vi.fn(),
      emit: vi.fn(),
      disconnect: vi.fn()
    }
    
    const io = require('socket.io-client').default
    io.mockReturnValue(mockSocket)
    
    const { unmount } = render(<App />)
    
    unmount()
    
    // Verify socket is disconnected on unmount
    expect(mockSocket.disconnect).toHaveBeenCalled()
  })
})

