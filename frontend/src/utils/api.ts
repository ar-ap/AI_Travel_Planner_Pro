import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || 120000) // 默认2分钟
})

// 创建一个专门用于长时间请求的API实例（AI生成等）
export const longRunningApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: 180000 // 3分钟，用于AI生成详细行程
})

// 为longRunningApi添加拦截器
longRunningApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

longRunningApi.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('=== API 请求拦截 ===')
    console.log('URL:', config.url)
    console.log('方法:', config.method)
    console.log('Token存在:', !!token)
    if (token) {
      console.log('Token长度:', token.length)
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.warn('[API] No token found in localStorage')
    }
    console.log('请求头:', config.headers)
    console.log('请求体:', config.data)
    console.log('=====================')
    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    console.log('=== API 响应拦截 ===')
    console.log('状态码:', response.status)
    console.log('响应头:', response.headers)
    console.log('响应类型:', typeof response.data)
    console.log('响应keys:', response.data ? Object.keys(response.data) : 'N/A')

    // 打印响应内容的结构
    if (typeof response.data === 'object' && response.data !== null) {
      console.log('完整响应:', JSON.stringify(response.data, null, 2))
    } else {
      console.log('响应内容:', response.data)
    }
    console.log('=====================')

    // 直接返回响应数据，让调用者处理
    return response.data
  },
  (error) => {
    console.error('=== API 响应错误 ===')
    console.error('错误对象:', error)
    console.error('错误状态:', error.response?.status)
    console.error('错误数据:', error.response?.data)
    console.error('=====================')

    // 处理401未授权错误
    if (error.response?.status === 401) {
      console.warn('[API] 收到401未授权错误')
      localStorage.removeItem('token')
      localStorage.removeItem('user')

      // 如果在浏览器环境中，重定向到登录页
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
