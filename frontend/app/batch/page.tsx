"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Zap, Play, CheckCircle2, XCircle, Download, Loader2 } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"

type Device = {
  name: string
  host: string
  device_type: string
}

type BatchResult = {
  device: string
  status: string
  output: string
}

type DeviceProgress = {
  device: string
  status: 'pending' | 'running' | 'success' | 'error'
  output?: string
}

export default function BatchPage() {
  const [devices, setDevices] = useState<Record<string, any>>({})
  const [selectedDevices, setSelectedDevices] = useState<string[]>([])
  const [command, setCommand] = useState("")
  const [results, setResults] = useState<BatchResult[]>([])
  const [progress, setProgress] = useState<DeviceProgress[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [progressPercent, setProgressPercent] = useState(0)

  useEffect(() => {
    fetch('http://localhost:8000/inventory/devices')
      .then(res => res.json())
      .then(data => setDevices(data))
      .catch(err => console.error('Failed to fetch devices:', err))
  }, [])

  const toggleDevice = (deviceName: string) => {
    setSelectedDevices(prev => 
      prev.includes(deviceName) 
        ? prev.filter(d => d !== deviceName)
        : [...prev, deviceName]
    )
  }

  const selectAll = () => {
    setSelectedDevices(Object.keys(devices))
  }

  const clearSelection = () => {
    setSelectedDevices([])
  }

  const selectByTag = (tag: string) => {
    const devicesWithTag = Object.entries(devices)
      .filter(([_, device]) => device.tags?.includes(tag))
      .map(([name, _]) => name)
    setSelectedDevices(devicesWithTag)
  }

  // Get all unique tags from all devices
  const allTags = Array.from(
    new Set(
      Object.values(devices).flatMap((device: any) => device.tags || [])
    )
  )

  const handleExecute = async () => {
    if (selectedDevices.length === 0) {
      setMessage("Please select at least one device")
      setTimeout(() => setMessage(""), 3000)
      return
    }
    if (!command) {
      setMessage("Please enter a command")
      setTimeout(() => setMessage(""), 3000)
      return
    }

    setLoading(true)
    setResults([])
    setProgressPercent(0)
    
    // Initialize progress tracking
    const initialProgress = selectedDevices.map(device => ({
      device,
      status: 'pending' as const
    }))
    setProgress(initialProgress)

    try {
      const res = await fetch('http://localhost:8000/batch/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_names: selectedDevices,
          command: command
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        setResults(data)
        setProgressPercent(100)
        setMessage(`Executed on ${selectedDevices.length} device(s)`)
        
        // Update progress with final results
        const finalProgress = data.map((result: BatchResult) => ({
          device: result.device,
          status: result.status === 'success' ? 'success' as const : 'error' as const,
          output: result.output
        }))
        setProgress(finalProgress)
        
        setTimeout(() => setMessage(""), 5000)
      }
    } catch (err) {
      console.error('Failed to execute command:', err)
      setMessage("Failed to execute command")
      setTimeout(() => setMessage(""), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (results.length === 0) return

    try {
      const res = await fetch('http://localhost:8000/batch/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results)
      })

      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `batch_results_${Date.now()}.zip`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('Download failed:', err)
      setMessage("Download failed")
      setTimeout(() => setMessage(""), 3000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Zap className="h-8 w-8" />
          Batch Operations
        </h1>
        <p className="text-muted-foreground">Run commands on multiple devices simultaneously</p>
      </div>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Device Selection</CardTitle>
            <CardDescription>
              {selectedDevices.length} of {Object.keys(devices).length} device(s) selected
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              <Button size="sm" variant="outline" onClick={selectAll}>
                Select All
              </Button>
              <Button size="sm" variant="outline" onClick={clearSelection}>
                Clear
              </Button>
              {allTags.length > 0 && (
                <>
                  <Separator orientation="vertical" className="h-8" />
                  {allTags.map(tag => (
                    <Button 
                      key={tag} 
                      size="sm" 
                      variant="outline"
                      onClick={() => selectByTag(tag)}
                    >
                      Tag: {tag}
                    </Button>
                  ))}
                </>
              )}
            </div>
            <Separator />
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {Object.entries(devices).map(([name, device]) => (
                <div
                  key={name}
                  className={`p-3 border rounded-lg cursor-pointer transition-all ${
                    selectedDevices.includes(name)
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => toggleDevice(name)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{name}</p>
                      <p className="text-sm text-muted-foreground">{device.host}</p>
                      {device.tags?.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {device.tags.map((tag: string) => (
                            <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <Badge variant="secondary">{device.device_type}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Command</CardTitle>
            <CardDescription>Enter the command to execute</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="e.g., show version"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              className="font-mono"
            />
            <Button 
              onClick={handleExecute} 
              disabled={loading || selectedDevices.length === 0}
              className="w-full"
            >
              <Play className="mr-2 h-4 w-4" />
              {loading ? 'Executing...' : 'Execute Command'}
            </Button>
            
            {results.length > 0 && (
              <Button 
                onClick={handleDownload}
                variant="outline"
                className="w-full"
              >
                <Download className="mr-2 h-4 w-4" />
                Download Results (.zip)
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {loading && progress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Execution Progress</CardTitle>
            <CardDescription>
              Processing {selectedDevices.length} device(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Progress value={progressPercent} className="w-full" />
            <div className="space-y-2">
              {progress.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  {item.status === 'pending' && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
                  {item.status === 'running' && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
                  {item.status === 'success' && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                  {item.status === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
                  <span className="font-medium">{item.device}</span>
                  <Badge variant={
                    item.status === 'success' ? 'default' : 
                    item.status === 'error' ? 'destructive' : 
                    'secondary'
                  }>
                    {item.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {results.length > 0 && !loading && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            <CardDescription>
              Command execution results
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {results.map((result, idx) => (
              <div key={idx} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {result.status === 'success' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <span className="font-medium">{result.device}</span>
                  </div>
                  <Badge variant={result.status === 'success' ? 'default' : 'destructive'}>
                    {result.status}
                  </Badge>
                </div>
                <pre className="bg-muted p-3 rounded text-sm font-mono overflow-x-auto max-h-[300px] overflow-y-auto">
                  {result.output}
                </pre>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
