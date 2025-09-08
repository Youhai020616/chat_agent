import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { 
  GlobeAltIcon,
  MagnifyingGlassIcon,
  PlayIcon 
} from '@heroicons/react/24/outline'

interface AnalysisForm {
  url: string
  locale: string
}

// 模拟 API 调用
const startAnalysis = async (data: AnalysisForm) => {
  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 模拟 API 响应
  return {
    run_id: `run_${Date.now()}`,
    status: 'pending',
    message: 'Analysis started successfully'
  }
}

export function Analysis() {
  const navigate = useNavigate()
  const [form, setForm] = useState<AnalysisForm>({
    url: '',
    locale: 'zh-CN'
  })

  const mutation = useMutation({
    mutationFn: startAnalysis,
    onSuccess: (data) => {
      toast.success('分析任务已启动！')
      navigate(`/results/${data.run_id}`)
    },
    onError: (error) => {
      toast.error('启动分析失败，请重试')
      console.error('Analysis error:', error)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!form.url) {
      toast.error('请输入网站 URL')
      return
    }

    // 验证 URL 格式
    try {
      new URL(form.url)
    } catch {
      toast.error('请输入有效的 URL')
      return
    }

    mutation.mutate(form)
  }

  const handleInputChange = (field: keyof AnalysisForm, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">网站 SEO & GEO 分析</h1>
        <p className="mt-2 text-gray-600">
          输入网站 URL，我们将为您提供全面的 SEO 和地理位置优化分析
        </p>
      </div>

      {/* 分析表单 */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* URL 输入 */}
          <div>
            <label className="label">
              <GlobeAltIcon className="inline h-5 w-5 mr-2" />
              网站 URL
            </label>
            <input
              type="url"
              value={form.url}
              onChange={(e) => handleInputChange('url', e.target.value)}
              placeholder="https://example.com"
              className="input-field"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              请输入完整的网站 URL，包括 http:// 或 https://
            </p>
          </div>

          {/* 语言/地区选择 */}
          <div>
            <label className="label">
              语言/地区
            </label>
            <select
              value={form.locale}
              onChange={(e) => handleInputChange('locale', e.target.value)}
              className="input-field"
            >
              <option value="zh-CN">中文 (简体)</option>
              <option value="zh-TW">中文 (繁体)</option>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
              <option value="ja-JP">日本語</option>
              <option value="ko-KR">한국어</option>
            </select>
          </div>

          {/* 提交按钮 */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn-primary flex items-center space-x-2 px-8 py-3 text-lg"
            >
              {mutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>启动分析中...</span>
                </>
              ) : (
                <>
                  <PlayIcon className="h-5 w-5" />
                  <span>开始分析</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* 分析说明 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-start space-x-3">
            <MagnifyingGlassIcon className="h-6 w-6 text-blue-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">SEO 分析</h3>
              <p className="mt-2 text-gray-600">
                全面分析网站的搜索引擎优化状况，包括关键词分析、内容优化、技术 SEO 和链接建设建议。
              </p>
              <ul className="mt-3 text-sm text-gray-500 space-y-1">
                <li>• 关键词研究和竞争分析</li>
                <li>• 页面内容和结构优化</li>
                <li>• 技术 SEO 问题检测</li>
                <li>• 内外链分析和建议</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-start space-x-3">
            <GlobeAltIcon className="h-6 w-6 text-green-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">GEO 优化</h3>
              <p className="mt-2 text-gray-600">
                专注于地理位置相关的搜索优化，提升本地搜索排名和地理相关性。
              </p>
              <ul className="mt-3 text-sm text-gray-500 space-y-1">
                <li>• 本地搜索优化分析</li>
                <li>• Google My Business 优化</li>
                <li>• 地理关键词策略</li>
                <li>• NAP 一致性检查</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
