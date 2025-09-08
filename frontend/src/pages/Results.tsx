import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  GlobeAltIcon,
  WrenchScrewdriverIcon,
  LinkIcon,
  DocumentTextIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

interface AnalysisResults {
  run: {
    id: string
    status: string
    progress: number
    started_at: string
    finished_at?: string
  }
  keyword_insights?: any
  technical_insights?: any
  geo_insights?: any
  serp_insights?: any
  action_plan?: any[]
}

// 模拟 API 调用
const fetchResults = async (runId: string): Promise<AnalysisResults> => {
  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  return {
    run: {
      id: runId,
      status: 'completed',
      progress: 100,
      started_at: '2025-09-08T10:30:00Z',
      finished_at: '2025-09-08T10:35:00Z'
    },
    keyword_insights: {
      current_keywords: [
        { keyword: 'SEO优化', frequency: 8, type: 'phrase' },
        { keyword: '网站分析', frequency: 6, type: 'phrase' },
        { keyword: '搜索引擎', frequency: 5, type: 'phrase' }
      ],
      keyword_gaps: [
        { keyword: '本地SEO', gap_type: 'competitor_coverage', priority: 'high' },
        { keyword: '移动优化', gap_type: 'semantic_coverage', priority: 'medium' }
      ],
      keyword_strategy: {
        primary_keywords: ['SEO优化', '网站分析'],
        secondary_keywords: ['搜索引擎', '关键词分析'],
        optimization_priorities: [
          { priority: 1, action: '优化主要关键词密度', impact: 'high' }
        ]
      }
    },
    technical_insights: {
      overall_score: 78,
      page_performance: {
        load_time: 2.3,
        performance_score: 85,
        issues: []
      },
      meta_tags: {
        title: { length: 45, issues: [] },
        description: { length: 0, issues: [{ type: 'missing_description', severity: 'high' }] },
        meta_score: 70
      },
      critical_issues: [
        {
          type: 'meta',
          severity: 'high',
          title: '缺少Meta Description',
          description: '页面缺少Meta描述，影响搜索结果展示'
        }
      ]
    },
    geo_insights: {
      geographic_entities: {
        cities: ['北京', '上海'],
        provinces: ['北京市']
      },
      nap_analysis: {
        consistency_score: 85,
        issues: ['发现多个不同的电话号码']
      },
      recommendations: [
        {
          category: 'nap_consistency',
          priority: 'high',
          title: '统一NAP信息',
          description: '确保所有平台上的公司信息一致'
        }
      ]
    },
    serp_insights: {
      analyzed_keywords: ['SEO优化', '网站分析'],
      local_search_opportunities: [
        {
          type: 'local_pack',
          keyword: 'SEO优化',
          opportunity: 'high',
          description: '关键词显示本地包结果，有很好的本地SEO机会'
        }
      ],
      competitor_analysis: {
        top_competitors: [
          { domain: 'competitor1.com', total_appearances: 8 },
          { domain: 'competitor2.com', total_appearances: 6 }
        ]
      }
    },
    action_plan: [
      {
        action: '添加Meta Description',
        category: 'technical',
        impact: 4,
        effort: 2,
        priority: 'high',
        description: '页面缺少Meta Description，建议添加150-160字符的描述'
      },
      {
        action: '统一NAP信息',
        category: 'geo',
        impact: 4,
        effort: 3,
        priority: 'high',
        description: '确保所有平台上的公司名称、地址、电话信息一致'
      },
      {
        action: '填补关键词缺口',
        category: 'keyword',
        impact: 4,
        effort: 3,
        priority: 'medium',
        description: '发现2个关键词缺口，建议增加相关内容'
      }
    ]
  }
}

export function Results() {
  const { runId } = useParams<{ runId: string }>()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: results, isLoading, error } = useQuery({
    queryKey: ['results', runId],
    queryFn: () => fetchResults(runId!),
    enabled: !!runId
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载分析结果中...</p>
        </div>
      </div>
    )
  }

  if (error || !results) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">加载失败</h3>
        <p className="mt-2 text-gray-600">无法加载分析结果，请稍后重试</p>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', name: '总览', icon: ChartBarIcon },
    { id: 'keyword', name: '关键词分析', icon: MagnifyingGlassIcon },
    { id: 'content', name: '内容分析', icon: DocumentTextIcon },
    { id: 'technical', name: '技术SEO', icon: WrenchScrewdriverIcon },
    { id: 'link', name: '链接分析', icon: LinkIcon },
    { id: 'competitor', name: '竞争分析', icon: UserGroupIcon },
    { id: 'geo', name: '地理优化', icon: GlobeAltIcon }
  ]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      {/* 分析状态 */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">分析结果</h1>
            <p className="text-gray-600">运行ID: {results.run.id}</p>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="h-5 w-5 text-green-500" />
            <span className="text-green-600 font-medium">分析完成</span>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {results.technical_insights?.overall_score || 0}
            </div>
            <div className="text-sm text-gray-600">总体SEO分数</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {results.action_plan?.length || 0}
            </div>
            <div className="text-sm text-gray-600">优化建议</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {results.keyword_insights?.current_keywords?.length || 0}
            </div>
            <div className="text-sm text-gray-600">发现关键词</div>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center py-2 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* 标签页内容 */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* 优化行动计划 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">优化行动计划</h2>
              <div className="space-y-4">
                {results.action_plan?.map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium text-gray-900">{item.action}</h3>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(item.priority)}`}>
                            {item.priority === 'high' ? '高优先级' : item.priority === 'medium' ? '中优先级' : '低优先级'}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-gray-600">{item.description}</p>
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                          <span>影响: {item.impact}/5</span>
                          <span>工作量: {item.effort}/5</span>
                          <span>类别: {item.category}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'keyword' && results.keyword_insights && (
          <div className="space-y-6">
            {/* 当前关键词 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">当前关键词</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.keyword_insights.current_keywords?.slice(0, 9).map((kw: any, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3">
                    <div className="font-medium text-gray-900">{kw.keyword}</div>
                    <div className="text-sm text-gray-600">频次: {kw.frequency}</div>
                    <div className="text-xs text-gray-500">{kw.type}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* 关键词缺口 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">关键词缺口</h2>
              <div className="space-y-3">
                {results.keyword_insights.keyword_gaps?.map((gap: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div>
                      <div className="font-medium text-gray-900">{gap.keyword}</div>
                      <div className="text-sm text-gray-600">{gap.gap_type}</div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(gap.priority)}`}>
                      {gap.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'technical' && results.technical_insights && (
          <div className="space-y-6">
            {/* 技术SEO分数 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">技术SEO评分</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {results.technical_insights.overall_score}
                  </div>
                  <div className="text-sm text-gray-600">总体分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {results.technical_insights.page_performance?.performance_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">性能分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {results.technical_insights.meta_tags?.meta_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">Meta标签分数</div>
                </div>
              </div>
            </div>

            {/* 关键问题 */}
            {results.technical_insights.critical_issues?.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">关键问题</h2>
                <div className="space-y-3">
                  {results.technical_insights.critical_issues.map((issue: any, index: number) => (
                    <div key={index} className="border-l-4 border-red-400 bg-red-50 p-4">
                      <div className="flex">
                        <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-red-800">{issue.title}</h3>
                          <p className="mt-1 text-sm text-red-700">{issue.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'content' && results.content_insights && (
          <div className="space-y-6">
            {/* 内容质量分数 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">内容质量评估</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {results.content_insights.content_quality_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">总体质量分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {results.content_insights.readability_analysis?.readability_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">可读性分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {results.content_insights.seo_optimization?.seo_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">SEO优化分数</div>
                </div>
              </div>
            </div>

            {/* 内容缺口 */}
            {results.content_insights.content_gaps?.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">内容缺口</h2>
                <div className="space-y-3">
                  {results.content_insights.content_gaps.map((gap: any, index: number) => (
                    <div key={index} className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
                      <div className="flex">
                        <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-yellow-800">{gap.gap_type}</h3>
                          <p className="mt-1 text-sm text-yellow-700">{gap.description}</p>
                          <p className="mt-1 text-xs text-yellow-600">{gap.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'link' && results.link_insights && (
          <div className="space-y-6">
            {/* 链接优化分数 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">链接分析</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {results.link_insights.link_optimization_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">链接优化分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {results.link_insights.internal_links_analysis?.total_internal_links || 0}
                  </div>
                  <div className="text-sm text-gray-600">内部链接数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {results.link_insights.external_links_analysis?.total_external_links || 0}
                  </div>
                  <div className="text-sm text-gray-600">外部链接数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {results.link_insights.link_quality_analysis?.overall_quality_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">链接质量分数</div>
                </div>
              </div>
            </div>

            {/* 链接建设机会 */}
            {results.link_insights.link_opportunities?.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">链接建设机会</h2>
                <div className="space-y-3">
                  {results.link_insights.link_opportunities.map((opp: any, index: number) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{opp.title}</h3>
                          <p className="mt-1 text-sm text-gray-600">{opp.description}</p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>影响: {opp.potential_impact}</span>
                            <span>工作量: {opp.effort_required}</span>
                          </div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(opp.priority)}`}>
                          {opp.priority}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'competitor' && results.competitor_insights && (
          <div className="space-y-6">
            {/* 竞争强度 */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">竞争环境分析</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">
                    {results.competitor_insights.competition_intensity?.intensity_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">竞争强度分数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {results.competitor_insights.identified_competitors?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">识别竞争对手</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900 capitalize">
                    {results.competitor_insights.competition_intensity?.overall_intensity || 'medium'}
                  </div>
                  <div className="text-sm text-gray-600">竞争级别</div>
                </div>
              </div>
            </div>

            {/* 主要竞争对手 */}
            {results.competitor_insights.identified_competitors?.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">主要竞争对手</h2>
                <div className="space-y-3">
                  {results.competitor_insights.identified_competitors.slice(0, 5).map((competitor: any, index: number) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-gray-900">{competitor.domain}</h3>
                          <p className="text-sm text-gray-600">出现次数: {competitor.appearances}</p>
                          <p className="text-xs text-gray-500">平均排名: {competitor.avg_position?.toFixed(1)}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900">
                            关键词: {competitor.keywords?.length || 0}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* SWOT分析 */}
            {results.competitor_insights.swot_analysis && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">SWOT分析</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-green-800 mb-2">优势 (Strengths)</h3>
                    <div className="space-y-2">
                      {results.competitor_insights.swot_analysis.strengths?.slice(0, 3).map((strength: any, index: number) => (
                        <div key={index} className="text-sm text-green-700 bg-green-50 p-2 rounded">
                          {strength.description}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-red-800 mb-2">劣势 (Weaknesses)</h3>
                    <div className="space-y-2">
                      {results.competitor_insights.swot_analysis.weaknesses?.slice(0, 3).map((weakness: any, index: number) => (
                        <div key={index} className="text-sm text-red-700 bg-red-50 p-2 rounded">
                          {weakness.description}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-blue-800 mb-2">机会 (Opportunities)</h3>
                    <div className="space-y-2">
                      {results.competitor_insights.swot_analysis.opportunities?.slice(0, 3).map((opportunity: any, index: number) => (
                        <div key={index} className="text-sm text-blue-700 bg-blue-50 p-2 rounded">
                          {opportunity.description}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-yellow-800 mb-2">威胁 (Threats)</h3>
                    <div className="space-y-2">
                      {results.competitor_insights.swot_analysis.threats?.slice(0, 3).map((threat: any, index: number) => (
                        <div key={index} className="text-sm text-yellow-700 bg-yellow-50 p-2 rounded">
                          {threat.description}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 其他标签页内容可以继续添加 */}
      </div>
    </div>
  )
}
