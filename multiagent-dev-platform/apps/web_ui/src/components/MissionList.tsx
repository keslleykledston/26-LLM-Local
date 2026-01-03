'use client'

import { Loader, CheckCircle, XCircle, Clock, AlertCircle, Wifi, WifiOff } from 'lucide-react'
import { useMissionSSE } from '@/hooks/useMissionSSE'

interface Mission {
  id: number
  title: string
  description: string
  status: string
  created_at: string
  updated_at: string
}

export default function MissionList() {
  const { missions, loading, error, isConnected, refresh } = useMissionSSE()

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'planning':
      case 'executing':
      case 'validating':
      case 'integrating':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-slate-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'planning':
      case 'executing':
      case 'validating':
      case 'integrating':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  if (error && missions.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <button
          onClick={refresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  if (missions.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <p className="text-slate-600 dark:text-slate-400">No missions yet. Create your first mission!</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* SSE Connection Status */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 text-sm">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-green-500" />
              <span className="text-green-600 dark:text-green-400">Live updates active</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-yellow-500" />
              <span className="text-yellow-600 dark:text-yellow-400">Reconnecting...</span>
            </>
          )}
        </div>
        <button
          onClick={refresh}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Refresh
        </button>
      </div>
      {missions.map((mission) => (
        <div
          key={mission.id}
          className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-start gap-3 flex-1">
              {getStatusIcon(mission.status)}
              <div className="flex-1">
                <h3 className="font-medium text-slate-900 dark:text-white">{mission.title}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                  {mission.description}
                </p>
              </div>
            </div>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(mission.status)}`}>
              {mission.status}
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 mt-3">
            <span>#{mission.id}</span>
            <span>Created {new Date(mission.created_at).toLocaleString()}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
