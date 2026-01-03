'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
import { api } from '@/lib/api'

interface MissionFormProps {
  onSuccess?: () => void
}

export default function MissionForm({ onSuccess }: MissionFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validações frontend
    if (!title || title.length < 3) {
      setError('Title must be at least 3 characters')
      return
    }
    if (!description || description.length < 10) {
      setError('Description must be at least 10 characters')
      return
    }

    setLoading(true)
    try {
      await api.post('/api/v1/missions/', {
        title,
        description,
        created_by: 'user',
      })
      setTitle('')
      setDescription('')
      setError('')
      onSuccess?.()
    } catch (error: any) {
      console.error('Failed to create mission:', error)
      const errorMsg =
        error?.payload?.detail?.[0]?.msg ||
        error?.payload?.detail ||
        error?.payload?.error ||
        error?.message ||
        'Failed to create mission. Please check your inputs.'
      setError(String(errorMsg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Mission Title
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add user authentication"
          className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Implement JWT-based authentication with login and signup endpoints. Include password hashing and token refresh..."
          rows={6}
          className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !title || !description}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-md font-medium transition-colors"
      >
        {loading ? (
          <span>Creating...</span>
        ) : (
          <>
            <Send className="w-4 h-4" />
            <span>Create Mission</span>
          </>
        )}
      </button>
    </form>
  )
}
