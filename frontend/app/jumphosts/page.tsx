"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield, Trash2, Plus } from "lucide-react"

type JumpHost = {
  host: string
  username: string
  password: string
  port: number
}

export default function JumpHostsPage() {
  const [jumphosts, setJumphosts] = useState<Record<string, JumpHost>>({})
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [message, setMessage] = useState("")
  
  const [formData, setFormData] = useState({
    name: "",
    host: "",
    username: "",
    password: "",
    port: 22
  })

  const fetchJumphosts = async () => {
    try {
      const res = await fetch('http://localhost:8000/jumphosts')
      const data = await res.json()
      setJumphosts(data)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch jump hosts:', err)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJumphosts()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch('http://localhost:8000/jumphosts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      if (res.ok) {
        setMessage("Jump host added successfully!")
        setFormData({ name: "", host: "", username: "", password: "", port: 22 })
        setShowForm(false)
        fetchJumphosts()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Failed to add jump host:', err)
    }
  }

  const handleDelete = async (name: string) => {
    try {
      const res = await fetch(`http://localhost:8000/jumphosts/${name}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        setMessage("Jump host deleted successfully!")
        fetchJumphosts()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Failed to delete jump host:', err)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Jump Hosts</h1>
          <p className="text-muted-foreground">Manage your bastion/jump host profiles</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Jump Host
        </Button>
      </div>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add New Jump Host</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Profile Name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
                <Input
                  placeholder="Host IP/Name"
                  value={formData.host}
                  onChange={(e) => setFormData({...formData, host: e.target.value})}
                  required
                />
                <Input
                  placeholder="Username"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
                <Input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
                <Input
                  type="number"
                  placeholder="Port"
                  value={formData.port}
                  onChange={(e) => setFormData({...formData, port: parseInt(e.target.value)})}
                  required
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save</Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Jump Host Profiles
          </CardTitle>
          <CardDescription>
            {Object.keys(jumphosts).length} profile(s) configured
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : Object.keys(jumphosts).length === 0 ? (
            <p className="text-sm text-muted-foreground">No jump hosts configured</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Username</TableHead>
                  <TableHead>Port</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(jumphosts).map(([name, jh]) => (
                  <TableRow key={name}>
                    <TableCell className="font-medium">{name}</TableCell>
                    <TableCell>{jh.host}</TableCell>
                    <TableCell>{jh.username}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{jh.port}</Badge>
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleDelete(name)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
