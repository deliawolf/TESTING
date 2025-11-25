"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield, LogIn, LogOut, Loader2 } from "lucide-react"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

type GatewayStatus = {
  connected: boolean
  status: string
  jumphost1?: string
  jumphost2?: string
}

type JumpHost = {
  host: string
  username: string
  port: number
}

export function GatewayControl() {
  const [status, setStatus] = useState<GatewayStatus>({ connected: false, status: 'disconnected' })
  const [jumphosts, setJumphosts] = useState<Record<string, JumpHost>>({})
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState("")
  
  const [formData, setFormData] = useState({
    jumphost1_profile: "",
    jumphost2_profile: ""
  })

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/gateway/status')
      const data = await res.json()
      setStatus(data)
    } catch (err) {
      console.error('Failed to fetch gateway status:', err)
    }
  }

  const fetchJumphosts = async () => {
    try {
      const res = await fetch('http://localhost:8000/jumphosts')
      const data = await res.json()
      setJumphosts(data)
    } catch (err) {
      console.error('Failed to fetch jump hosts:', err)
    }
  }

  useEffect(() => {
    fetchStatus()
    fetchJumphosts()
    const interval = setInterval(fetchStatus, 5000) // Check status every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.jumphost1_profile) {
      setMessage("Please select a jump host")
      setTimeout(() => setMessage(""), 3000)
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/gateway/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (res.ok) {
        setMessage("Gateway connected successfully!")
        fetchStatus()
        setOpen(false)
        setTimeout(() => setMessage(""), 3000)
      } else {
        const error = await res.json()
        setMessage(error.detail || "Connection failed")
        setTimeout(() => setMessage(""), 5000)
      }
    } catch (err) {
      setMessage("Failed to connect to gateway")
      setTimeout(() => setMessage(""), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/gateway/disconnect', {
        method: 'POST'
      })
      
      if (res.ok) {
        setMessage("Gateway disconnected")
        fetchStatus()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      setMessage("Failed to disconnect")
      setTimeout(() => setMessage(""), 3000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {status.connected ? (
        <>
          <Badge variant="default" className="flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Gateway: Connected
          </Badge>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleDisconnect}
            disabled={loading}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogOut className="h-4 w-4" />}
          </Button>
        </>
      ) : (
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" size="sm">
              <Shield className="mr-2 h-4 w-4" />
              Connect Gateway
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Gateway Connection</SheetTitle>
              <SheetDescription>
                Establish a persistent connection through jump hosts
              </SheetDescription>
            </SheetHeader>
            
            {message && (
              <Alert className="mt-4">
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-lg">Jump Host Chain</CardTitle>
                <CardDescription>Select your jump host configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleConnect} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Jump Host 1 (Required)
                    </label>
                    <select
                      className="w-full p-2 border rounded-md"
                      value={formData.jumphost1_profile}
                      onChange={(e) => setFormData({...formData, jumphost1_profile: e.target.value})}
                      required
                    >
                      <option value="">Select jump host...</option>
                      {Object.keys(jumphosts).map(name => (
                        <option key={name} value={name}>{name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Jump Host 2 (Optional)
                    </label>
                    <select
                      className="w-full p-2 border rounded-md"
                      value={formData.jumphost2_profile}
                      onChange={(e) => setFormData({...formData, jumphost2_profile: e.target.value})}
                    >
                      <option value="">None (Direct)</option>
                      {Object.keys(jumphosts).map(name => (
                        <option key={name} value={name}>{name}</option>
                      ))}
                    </select>
                  </div>

                  <Button type="submit" disabled={loading} className="w-full">
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <LogIn className="mr-2 h-4 w-4" />
                        Connect
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </SheetContent>
        </Sheet>
      )}
    </div>
  )
}
