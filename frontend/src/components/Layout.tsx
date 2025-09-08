import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  ChartBarIcon, 
  DocumentMagnifyingGlassIcon,
  PresentationChartLineIcon 
} from '@heroicons/react/24/outline'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: '仪表盘', href: '/', icon: HomeIcon },
  { name: '批量分析', href: '/analysis', icon: DocumentMagnifyingGlassIcon },
  { name: 'KPI 监控', href: '/kpi', icon: PresentationChartLineIcon },
]

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 侧边栏 */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <h1 className="text-xl font-bold text-gradient">
            SEO & GEO 优化系统
          </h1>
        </div>
        
        <nav className="mt-8 px-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`
                      flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200
                      ${isActive 
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>

      {/* 主内容区域 */}
      <div className="pl-64">
        {/* 顶部导航栏 */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-gray-900">
                {navigation.find(item => item.href === location.pathname)?.name || '页面'}
              </h2>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-600">系统正常</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
