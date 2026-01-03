'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { Server, RefreshCw, ShieldAlert } from 'lucide-react'
import { api } from '@/lib/api'

interface Device {
  id: number
  name: string
  vendor: string
  platform: string
  host: string
  port: number
  username: string
  has_password: boolean
  has_enable_password: boolean
  last_error?: string | null
}

interface BgpPeer {
  peer: string
  as: string
  msg_rcvd: string
  msg_sent: string
  outq: string
  up_down: string
  state: string
  pref_rcv: string
}

interface BgpResponse {
  device_id: number
  vendor: string
  platform: string
  raw: string
  peers: BgpPeer[]
}

const platformOptions = [
  { value: 'huawei', label: 'Huawei (VRP)' },
  { value: 'cisco_ios', label: 'Cisco IOS' },
  { value: 'cisco_xe', label: 'Cisco IOS-XE' },
  { value: 'cisco_xr', label: 'Cisco IOS-XR' },
  { value: 'juniper', label: 'Juniper Junos' },
  { value: 'mikrotik_v6', label: 'MikroTik v6' },
  { value: 'mikrotik_v7', label: 'MikroTik v7' },
]

const vendorFromPlatform = (platform: string) => {
  if (platform.startsWith('cisco')) return 'cisco'
  if (platform.startsWith('mikrotik')) return 'mikrotik'
  return platform
}

export default function DeviceManager() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [name, setName] = useState('')
  const [platform, setPlatform] = useState(platformOptions[0].value)
  const [host, setHost] = useState('')
  const [port, setPort] = useState('22')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [enablePassword, setEnablePassword] = useState('')

  const [activeDeviceId, setActiveDeviceId] = useState<number | null>(null)
  const [queryPassword, setQueryPassword] = useState('')
  const [queryEnablePassword, setQueryEnablePassword] = useState('')
  const [bgpResponse, setBgpResponse] = useState<BgpResponse | null>(null)
  const [queryLoading, setQueryLoading] = useState(false)
  const [queryError, setQueryError] = useState('')

  const fetchDevices = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.get('/api/v1/devices/')
      setDevices(data)
      setError('')
    } catch (err: any) {
      setError(err?.message || 'Failed to load devices')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDevices()
  }, [fetchDevices])

  const handleCreate = async () => {
    if (!name || !host || !username) {
      setError('Preencha nome, host e usuário.')
      return
    }

    setLoading(true)
    try {
      await api.post('/api/v1/devices/', {
        name,
        vendor: vendorFromPlatform(platform),
        platform,
        host,
        port: Number(port),
        username,
        password: password || undefined,
        enable_password: enablePassword || undefined,
      })
      setName('')
      setHost('')
      setUsername('')
      setPassword('')
      setEnablePassword('')
      setError('')
      await fetchDevices()
    } catch (err: any) {
      setError(err?.message || 'Failed to create device')
    } finally {
      setLoading(false)
    }
  }

  const activeDevice = useMemo(
    () => devices.find((device) => device.id === activeDeviceId) || null,
    [devices, activeDeviceId]
  )

  const handleQuery = async (device: Device) => {
    setQueryLoading(true)
    setQueryError('')
    setBgpResponse(null)
    try {
      const payload: any = {}
      if (queryPassword) payload.password = queryPassword
      if (queryEnablePassword) payload.enable_password = queryEnablePassword
      const data = await api.post(`/api/v1/devices/${device.id}/bgp/peers`, payload)
      setBgpResponse(data)
      setQueryPassword('')
      setQueryEnablePassword('')
    } catch (err: any) {
      setQueryError(err?.message || 'Falha ao consultar BGP.')
    } finally {
      setQueryLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-500" />
            Novo Dispositivo
          </h3>
          <div className="space-y-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nome do dispositivo"
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
            />
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
            >
              {platformOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <input
              value={host}
              onChange={(e) => setHost(e.target.value)}
              placeholder="IP ou hostname"
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                value={port}
                onChange={(e) => setPort(e.target.value)}
                placeholder="Porta"
                className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
              />
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Usuário"
                className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
              />
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Senha (opcional)"
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
            />
            <input
              type="password"
              value={enablePassword}
              onChange={(e) => setEnablePassword(e.target.value)}
              placeholder="Senha enable (opcional)"
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
            />
            {error && (
              <div className="text-xs text-red-600 dark:text-red-400">{error}</div>
            )}
            <button
              onClick={handleCreate}
              disabled={loading}
              className="w-full px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-md"
            >
              {loading ? 'Salvando...' : 'Salvar dispositivo'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Inventário
            </h3>
            <button
              onClick={fetchDevices}
              className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-700"
            >
              <RefreshCw className="w-3 h-3" />
              Atualizar
            </button>
          </div>

          {loading && devices.length === 0 ? (
            <div className="text-sm text-slate-500">Carregando...</div>
          ) : devices.length === 0 ? (
            <div className="text-sm text-slate-500">Nenhum dispositivo cadastrado.</div>
          ) : (
            <div className="space-y-3">
              {devices.map((device) => (
                <div
                  key={device.id}
                  className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 bg-white dark:bg-slate-800"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-white">
                        {device.name}
                      </div>
                      <div className="text-xs text-slate-500">
                        {device.host}:{device.port} · {device.platform} · {device.username}
                      </div>
                    </div>
                    <button
                      onClick={() =>
                        setActiveDeviceId(activeDeviceId === device.id ? null : device.id)
                      }
                      className="px-3 py-1.5 text-xs font-medium rounded-md bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
                    >
                      Consultar BGP
                    </button>
                  </div>

                  {device.last_error && (
                    <div className="mt-2 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3" />
                      {device.last_error}
                    </div>
                  )}

                  {activeDeviceId === device.id && (
                    <div className="mt-4 space-y-3">
                      {!device.has_password && (
                        <input
                          type="password"
                          value={queryPassword}
                          onChange={(e) => setQueryPassword(e.target.value)}
                          placeholder="Senha do dispositivo"
                          className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
                        />
                      )}
                      {!device.has_enable_password && (
                        <input
                          type="password"
                          value={queryEnablePassword}
                          onChange={(e) => setQueryEnablePassword(e.target.value)}
                          placeholder="Senha enable (Cisco)"
                          className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-sm"
                        />
                      )}
                      {queryError && (
                        <div className="text-xs text-red-600 dark:text-red-400">{queryError}</div>
                      )}
                      <button
                        onClick={() => handleQuery(device)}
                        disabled={queryLoading}
                        className="px-3 py-2 text-xs font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700"
                      >
                        {queryLoading ? 'Consultando...' : 'Executar comando'}
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {bgpResponse && (
        <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 bg-white dark:bg-slate-800">
          <div className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
            BGP Peers · {bgpResponse.platform}
          </div>
          {bgpResponse.peers.length === 0 ? (
            <pre className="text-xs text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
              {bgpResponse.raw}
            </pre>
          ) : (
            <div className="overflow-auto">
              <table className="min-w-full text-xs text-slate-700 dark:text-slate-200">
                <thead>
                  <tr className="text-left border-b border-slate-200 dark:border-slate-700">
                    <th className="py-2 pr-3">Peer</th>
                    <th className="py-2 pr-3">AS</th>
                    <th className="py-2 pr-3">MsgRcvd</th>
                    <th className="py-2 pr-3">MsgSent</th>
                    <th className="py-2 pr-3">OutQ</th>
                    <th className="py-2 pr-3">Up/Down</th>
                    <th className="py-2 pr-3">State</th>
                    <th className="py-2 pr-3">PrefRcv</th>
                  </tr>
                </thead>
                <tbody>
                  {bgpResponse.peers.map((peer, index) => (
                    <tr key={`${peer.peer}-${index}`} className="border-b border-slate-100 dark:border-slate-700">
                      <td className="py-1 pr-3">{peer.peer}</td>
                      <td className="py-1 pr-3">{peer.as}</td>
                      <td className="py-1 pr-3">{peer.msg_rcvd}</td>
                      <td className="py-1 pr-3">{peer.msg_sent}</td>
                      <td className="py-1 pr-3">{peer.outq}</td>
                      <td className="py-1 pr-3">{peer.up_down}</td>
                      <td className="py-1 pr-3">{peer.state}</td>
                      <td className="py-1 pr-3">{peer.pref_rcv}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
