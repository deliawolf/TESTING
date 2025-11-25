"use client"

import { useEffect, useState } from "react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { AlertCircle, RefreshCw } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function BackendHealthCheck() {
  const [isHealthy, setIsHealthy] = useState(true)
  const [checking, setChecking] = useState(false)

  const checkBackend = async () => {
    setChecking(true)
    try {
      const res = await fetch(`${API_URL}/health`, {
        signal: AbortSignal.timeout(5000)
      })
      setIsHealthy(res.ok)
    } catch (err) {
      setIsHealthy(false)
    } finally {
      setChecking(false)
    }
  }

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000) // Check every 30s
    return () => clearInterval(interval)
  }, [])

  if (isHealthy) return null

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Backend Connection Lost</AlertTitle>
      <AlertDescription className="flex items-center justify-between">
        <span>Cannot connect to the backend API at {API_URL}. Please check if the server is running.</span>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={checkBackend}
          disabled={checking}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${checking ? 'animate-spin' : ''}`} />
          Retry
        </Button>
      </AlertDescription>
    </Alert>
  )
}
