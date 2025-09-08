import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EyeIcon,
  CursorArrowRaysIcon,
  MapPinIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// 模拟 API 调用
const fetchKPIData = async () => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  return {
    overview: {
      total_clicks: 15000,
      total_impressions: 150000,
      avg_ctr: 0.10,
      avg_position: 4.8,
      core_web_vitals_score: 82
    },
    trends: [
      {
        metric: 'organic_traffic',
        values: [
          { date: '2025-09-01', value: 1000 },
          { date: '2025-09-02', value: 1100 },
          { date: '2025-09-03', value: 1050 },
          { date: '2025-09-04', value: 1200 },
          { date: '2025-09-05', value: 1150 },
          { date: '2025-09-06', value: 1300 },
          { date: '2025-09-07', value: 1250 },
          { date: '2025-09-08', value: 1400 }
        ],
        trend: 'up',
        change_percentage: 20.0
      },
      {
        metric: 'average_position',
        values: [
          { date: '2025-09-01', value: 5.2 },
          { date: '2025-09-02', value: 5.1 },
          { date: '2025-09-03', value: 5.0 },
          { date: '2025-09-04', value: 4.9 },
          { date: '2025-09-05', value: 4.8 },
          { date: '2025-09-06', value: 4.7 },
          { date: '2025-09-07', value: 4.8 },
          { date: '2025-09-08', value: 4.6 }
        ],
        trend: 'up',
        change_percentage: -11.5
      }
    ],
    recent_changes: [
      {
        metric: 'Organic Traffic',
        change: '+15%',
        period: 'Last 7 days',
        trend: 'positive'
      },
      {
        metric: 'Page Speed',
        change: '+8%',
        period: 'Last 30 days',
        trend: 'positive'
      },
      {
        metric: 'Local Visibility',
        change: '+12%',
        period: 'Last 14 days',
        trend: 'positive'
      },
      {
        metric: 'Click-through Rate',
        change: '-3%',
        period: 'Last 7 days',
        trend: 'negative'
      }
    ],
    top_keywords: [
      { keyword: 'SEO优化', position: 3, change: '+2', clicks: 450, impressions: 5200 },
      { keyword: '网站分析', position: 5, change: '-1', clicks: 320, impressions: 4100 },
      { keyword: '本地SEO', position: 7, change: '+3', clicks: 280, impressions: 3800 },
      { keyword: '关键词研究', position: 4, change: '0', clicks: 380, impressions: 4500 },
      { keyword: '搜索引擎优化', position: 6, change: '+1', clicks: 290, impressions: 3900 }
    ]
  }
}

export function KPI() {
  const [selectedMetric, setSelectedMetric] = useState('organic_traffic')
  const [timeRange, setTimeRange] = useState('7d')

  const { data: kpiData, isLoading } = useQuery({
    queryKey: ['kpi-data'],
    queryFn: fetchKPIData
  })

  if (isLoading || !kpiData) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载 KPI 数据中...</p>
        </div>
      </div>
    )
  }

  const metricOptions = [
    { id: 'organic_traffic', name: '自然流量', icon: TrendingUpIcon },
    { id: 'average_position', name: '平均排名', icon: ChartBarIcon }
  ]

  const currentTrend = kpiData.trends.find(t => t.metric === selectedMetric)

  const formatValue = (value: number, metric: string) => {
    if (metric === 'average_position') {
      return value.toFixed(1)
    }
    return value.toLocaleString()
  }

  const getChangeColor = (trend: string) => {
    return trend === 'positive' ? 'text-green-600' : 'text-red-600'
  }

  const getChangeIcon = (trend: string) => {
    return trend === 'positive' ? TrendingUpIcon : TrendingDownIcon
  }

  return (
    <div className="space-y-6">
      {/* KPI 概览 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="card text-center">
          <EyeIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {kpiData.overview.total_impressions.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">总展示次数</div>
        </div>

        <div className="card text-center">
          <CursorArrowRaysIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {kpiData.overview.total_clicks.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">总点击次数</div>
        </div>

        <div className="card text-center">
          <ChartBarIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {(kpiData.overview.avg_ctr * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">平均点击率</div>
        </div>

        <div className="card text-center">
          <MapPinIcon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {kpiData.overview.avg_position.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">平均排名</div>
        </div>

        <div className="card text-center">
          <StarIcon className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {kpiData.overview.core_web_vitals_score}
          </div>
          <div className="text-sm text-gray-600">Core Web Vitals</div>
        </div>
      </div>

      {/* 趋势图表 */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">性能趋势</h2>
          <div className="flex items-center space-x-4">
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="input-field w-auto"
            >
              {metricOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="input-field w-auto"
            >
              <option value="7d">最近 7 天</option>
              <option value="30d">最近 30 天</option>
              <option value="90d">最近 90 天</option>
            </select>
          </div>
        </div>

        {currentTrend && (
          <div className="mb-4">
            <div className="flex items-center space-x-2">
              <span className="text-lg font-medium text-gray-900">
                {metricOptions.find(m => m.id === selectedMetric)?.name}
              </span>
              <span className={`flex items-center text-sm font-medium ${
                currentTrend.change_percentage > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {currentTrend.change_percentage > 0 ? (
                  <TrendingUpIcon className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDownIcon className="h-4 w-4 mr-1" />
                )}
                {Math.abs(currentTrend.change_percentage).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={currentTrend?.values || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
              />
              <YAxis 
                tickFormatter={(value) => formatValue(value, selectedMetric)}
              />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
                formatter={(value: number) => [formatValue(value, selectedMetric), metricOptions.find(m => m.id === selectedMetric)?.name]}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近变化 */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">最近变化</h2>
          <div className="space-y-4">
            {kpiData.recent_changes.map((change, index) => {
              const ChangeIcon = getChangeIcon(change.trend)
              return (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <ChangeIcon className={`h-5 w-5 ${getChangeColor(change.trend)}`} />
                    <div>
                      <div className="font-medium text-gray-900">{change.metric}</div>
                      <div className="text-sm text-gray-600">{change.period}</div>
                    </div>
                  </div>
                  <div className={`font-semibold ${getChangeColor(change.trend)}`}>
                    {change.change}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* 热门关键词 */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">热门关键词</h2>
          <div className="space-y-3">
            {kpiData.top_keywords.map((keyword, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{keyword.keyword}</div>
                  <div className="text-sm text-gray-600">
                    点击: {keyword.clicks} | 展示: {keyword.impressions}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">#{keyword.position}</div>
                  <div className={`text-sm font-medium ${
                    keyword.change.startsWith('+') ? 'text-green-600' : 
                    keyword.change.startsWith('-') ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {keyword.change !== '0' ? keyword.change : '无变化'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
