'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export function useMissionSSE() {
  const [missions, setMissions] = useState<Mission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch initial missions via REST API
  const fetchInitialMissions = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/missions/?limit=20`)
      if (!response.ok) throw new Error('Failed to fetch missions')
      const data = await response.json()
      setMissions(data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch initial missions:', err)
      setError('Failed to load missions')
    } finally {
      setLoading(false)
    }
  }, [])

  // Connect to SSE stream
  const connectSSE = useCallback(() => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    try {
      const eventSource = new EventSource(`${API_URL}/api/v1/missions/stream`)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        console.log('✅ SSE connection established')
        setIsConnected(true)
        setError(null)
      }

      eventSource.onmessage = (event) => {
        try {
          const mission = JSON.parse(event.data)

          // Update or add mission in state
          setMissions((prevMissions) => {
            const existingIndex = prevMissions.findIndex((m) => m.id === mission.id)

            if (existingIndex >= 0) {
              // Update existing mission
              const updated = [...prevMissions]
              updated[existingIndex] = mission
              return updated
            } else {
              // Add new mission at the beginning
              return [mission, ...prevMissions]
            }
          })
        } catch (err) {
          console.error('Failed to parse SSE message:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('SSE connection error:', err)
        setIsConnected(false)
        eventSource.close()

        // Attempt to reconnect after 5 seconds
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect SSE...')
          connectSSE()
        }, 5000)
      }
    } catch (err) {
      console.error('Failed to create SSE connection:', err)
      setError('Connection failed')
    }
  }, [])

  // Initialize: fetch initial data and connect to SSE
  useEffect(() => {
    fetchInitialMissions().then(() => {
      connectSSE()
    })

    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        console.log('🔌 Closing SSE connection')
        eventSourceRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [fetchInitialMissions, connectSSE])

  // Manual refresh function (fallback)
  const refresh = useCallback(async () => {
    await fetchInitialMissions()
  }, [fetchInitialMissions])

  return {
    missions,
    loading,
    error,
    isConnected,
    refresh,
  }
}
