'use client'

import { useState, useCallback, useEffect } from 'react'
import { CheckCircle, XCircle, Clock, Loader, AlertCircle, Calendar, User } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
const PAGE_SIZE = 20
const IN_PROGRESS_STATUSES = ['planning', 'executing', 'validating', 'integrating']

interface Mission {
  id: number
  title: string
  description: string
  status: string
  created_at: string
  updated_at: string
  completed_at?: string | null
  created_by?: string | null
}

interface MissionHistoryProps {
  initialFilter?: string
}

export default function MissionHistory({ initialFilter = 'all' }: MissionHistoryProps) {
  const [filter, setFilter] = useState<string>(initialFilter)
  const [missions, setMissions] = useState<Mission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null)

  const getStatusParam = (currentFilter: string) => {
    if (currentFilter === 'all') return null
    if (currentFilter === 'in_progress') return IN_PROGRESS_STATUSES.join(',')
    return currentFilter
  }

  const fetchMissions = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('limit', String(PAGE_SIZE + 1))
      params.set('offset', String(page * PAGE_SIZE))

      const statusParam = getStatusParam(filter)
      if (statusParam) {
        params.set('status', statusParam)
      }

      const response = await fetch(`${API_URL}/api/v1/missions/?${params.toString()}`)
      if (!response.ok) throw new Error('Failed to fetch missions')

      const data: Mission[] = await response.json()
      const hasExtra = data.length > PAGE_SIZE

      setHasMore(hasExtra)
      setMissions(hasExtra ? data.slice(0, PAGE_SIZE) : data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch missions:', err)
      setMissions([])
      setHasMore(false)
      setError('Failed to load missions')
    } finally {
      setLoading(false)
    }
  }, [filter, page])

  useEffect(() => {
    fetchMissions()
  }, [fetchMissions])

  const handleFilterChange = (nextFilter: string) => {
    if (nextFilter === filter) return
    setFilter(nextFilter)
    setPage(0)
    setSelectedMission(null)
  }

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
      case 'cancelled':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
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
      case 'cancelled':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'planning':
      case 'executing':
      case 'validating':
      case 'integrating':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const getDuration = (mission: Mission) => {
    const start = new Date(mission.created_at)
    const end = mission.completed_at ? new Date(mission.completed_at) : new Date()
    const diffMs = end.getTime() - start.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffSecs = Math.floor((diffMs % 60000) / 1000)

    if (diffMins > 0) {
      return `${diffMins}m ${diffSecs}s`
    }
    return `${diffSecs}s`
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
          onClick={fetchMissions}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filtros */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleFilterChange('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          Todas
        </button>
        <button
          onClick={() => handleFilterChange('completed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'completed'
              ? 'bg-green-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          Completadas
        </button>
        <button
          onClick={() => handleFilterChange('failed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'failed'
              ? 'bg-red-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          Falhadas
        </button>
        <button
          onClick={() => handleFilterChange('in_progress')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'in_progress'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          Em Progresso
        </button>
      </div>

      {/* Lista de Missões */}
      {missions.length === 0 ? (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">
            Nenhuma missão encontrada com esse filtro
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {missions.map((mission) => (
            <div
              key={mission.id}
              onClick={() => setSelectedMission(selectedMission?.id === mission.id ? null : mission)}
              className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-3 flex-1">
                  {getStatusIcon(mission.status)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-slate-900 dark:text-white">
                        {mission.title}
                      </h3>
                      <span className="text-xs text-slate-500">#{mission.id}</span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
                      {mission.description}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(mission.status)}`}>
                  {mission.status}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 mt-3">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(mission.created_at)}</span>
                </div>
                {mission.created_by && (
                  <div className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    <span>{mission.created_by}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{getDuration(mission)}</span>
                </div>
              </div>

              {/* Detalhes Expandidos */}
              {selectedMission?.id === mission.id && (
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <dl className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <dt className="font-medium text-slate-700 dark:text-slate-300">Status:</dt>
                      <dd className="text-slate-600 dark:text-slate-400">{mission.status}</dd>
                    </div>
                    <div>
                      <dt className="font-medium text-slate-700 dark:text-slate-300">Criada em:</dt>
                      <dd className="text-slate-600 dark:text-slate-400">{formatDate(mission.created_at)}</dd>
                    </div>
                    <div>
                      <dt className="font-medium text-slate-700 dark:text-slate-300">Atualizada em:</dt>
                      <dd className="text-slate-600 dark:text-slate-400">{formatDate(mission.updated_at)}</dd>
                    </div>
                    {mission.completed_at && (
                      <div>
                        <dt className="font-medium text-slate-700 dark:text-slate-300">Completada em:</dt>
                        <dd className="text-slate-600 dark:text-slate-400">{formatDate(mission.completed_at)}</dd>
                      </div>
                    )}
                    <div className="col-span-2">
                      <dt className="font-medium text-slate-700 dark:text-slate-300 mb-1">Descrição Completa:</dt>
                      <dd className="text-slate-600 dark:text-slate-400">{mission.description}</dd>
                    </div>
                  </dl>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Paginação */}
      {missions.length > 0 && (
        <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setPage(prev => Math.max(0, prev - 1))}
            disabled={page === 0}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              page === 0
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed dark:bg-slate-800 dark:text-slate-600'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            Anterior
          </button>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Página {page + 1}
          </span>
          <button
            onClick={() => setPage(prev => prev + 1)}
            disabled={!hasMore}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              !hasMore
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed dark:bg-slate-800 dark:text-slate-600'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  )
}
