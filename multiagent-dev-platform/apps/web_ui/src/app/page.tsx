'use client'

import { useState, useEffect } from 'react'
import { Play, Activity, Database, Cloud, CloudOff } from 'lucide-react'
import MissionForm from '@/components/MissionForm'
import MissionList from '@/components/MissionList'
import MissionHistory from '@/components/MissionHistory'
import DeviceManager from '@/components/DeviceManager'
import { api } from '@/lib/api'

export default function Home() {
  const [health, setHealth] = useState<any>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [activeTab, setActiveTab] = useState<'missions' | 'history' | 'devices'>('missions')

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const data = await api.get('/api/v1/health/')
      setHealth(data)
    } catch (error) {
      console.error('Health check failed:', error)
    }
  }

  const handleMissionCreated = () => {
    setRefreshKey(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Activity className="text-blue-500" />
                Multiagent Dev Platform
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                Local-first development powered by Ollama
              </p>
            </div>

            {/* Health Status */}
            {health && (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    health.services?.ollama === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-sm text-slate-600 dark:text-slate-400">Ollama</span>
                </div>
                <div className="flex items-center gap-2">
                  <Database className={`w-4 h-4 ${
                    health.services?.qdrant === 'healthy' ? 'text-green-500' : 'text-red-500'
                  }`} />
                  <span className="text-sm text-slate-600 dark:text-slate-400">Qdrant</span>
                </div>
                <div className="flex items-center gap-2">
                  {health.status === 'healthy' ? (
                    <CloudOff className="w-4 h-4 text-green-500" />
                  ) : (
                    <Cloud className="w-4 h-4 text-yellow-500" />
                  )}
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    {health.status === 'healthy' ? 'Offline-first' : 'Degraded'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Create Mission */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                <Play className="w-5 h-5 text-blue-500" />
                Create Mission
              </h2>
              <MissionForm onSuccess={handleMissionCreated} />
            </div>
          </div>

          {/* Right Column - Mission List */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  {activeTab === 'missions' ? 'Missions' : 'Mission History'}
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActiveTab('missions')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      activeTab === 'missions'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    Missions
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      activeTab === 'history'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    History
                  </button>
                  <button
                    onClick={() => setActiveTab('devices')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      activeTab === 'devices'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    Devices
                  </button>
                </div>
              </div>
              {activeTab === 'missions' ? (
                <MissionList key={refreshKey} />
              ) : activeTab === 'history' ? (
                <MissionHistory initialFilter="all" />
              ) : (
                <DeviceManager />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
