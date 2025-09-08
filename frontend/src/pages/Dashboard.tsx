import React from 'react'
import { Link } from 'react-router-dom'
import { 
  DocumentMagnifyingGlassIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline'

const stats = [
  { name: '总分析次数', value: '1,234', icon: DocumentMagnifyingGlassIcon, color: 'text-blue-600' },
  { name: '本月分析', value: '89', icon: ChartBarIcon, color: 'text-green-600' },
  { name: '进行中任务', value: '3', icon: ClockIcon, color: 'text-yellow-600' },
  { name: '已完成任务', value: '156', icon: CheckCircleIcon, color: 'text-purple-600' },
]

const recentAnalyses = [
  {
    id: '1',
    url: 'https://example.com',
    status: 'completed',
    progress: 100,
    createdAt: '2025-09-08T10:30:00Z',
    duration: '2m 34s'
  },
  {
    id: '2', 
    url: 'https://demo.com',
    status: 'running',
    progress: 65,
    createdAt: '2025-09-08T10:25:00Z',
    duration: '1m 45s'
  },
  {
    id: '3',
    url: 'https://test.com', 
    status: 'pending',
    progress: 0,
    createdAt: '2025-09-08T10:20:00Z',
    duration: '-'
  }
]

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* 欢迎区域 */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              欢迎使用 SEO & GEO 优化系统
            </h1>
            <p className="mt-2 text-gray-600">
              基于 AI 的智能化网站优化分析平台，提供全面的 SEO 和地理位置优化建议
            </p>
          </div>
          <Link
            to="/analysis"
            className="btn-primary"
          >
            开始新分析
          </Link>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className={`h-8 w-8 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 最近分析 */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">最近分析</h2>
          <Link to="/analysis" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            查看全部
          </Link>
        </div>
        
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  网站
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  进度
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  创建时间
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  耗时
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">操作</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentAnalyses.map((analysis) => (
                <tr key={analysis.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {analysis.url}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`
                      inline-flex px-2 py-1 text-xs font-semibold rounded-full
                      ${analysis.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                      ${analysis.status === 'running' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${analysis.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
                    `}>
                      {analysis.status === 'completed' && '已完成'}
                      {analysis.status === 'running' && '进行中'}
                      {analysis.status === 'pending' && '等待中'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${analysis.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{analysis.progress}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {new Date(analysis.createdAt).toLocaleString('zh-CN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {analysis.duration}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {analysis.status === 'completed' ? (
                      <Link
                        to={`/results/${analysis.id}`}
                        className="text-blue-600 hover:text-blue-700"
                      >
                        查看结果
                      </Link>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
