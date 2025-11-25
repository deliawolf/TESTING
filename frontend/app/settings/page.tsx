"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Key, Trash2, Plus } from "lucide-react"
import { Separator } from "@/components/ui/separator"

type Credential = {
  username: string
  password: string
  secret?: string
}

export default function SettingsPage() {
  const [credentials, setCredentials] = useState<Record<string, Credential>>({})
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [message, setMessage] = useState("")
  
  const [formData, setFormData] = useState({
    name: "",
    username: "",
    password: "",
    secret: ""
  })

  const fetchCredentials = async () => {
    try {
      const res = await fetch('http://localhost:8000/credentials')
      const data = await res.json()
      setCredentials(data)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch credentials:', err)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCredentials()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch('http://localhost:8000/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      if (res.ok) {
        setMessage("Credential added successfully!")
        setFormData({ name: "", username: "", password: "", secret: "" })
        setShowForm(false)
        fetchCredentials()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Failed to add credential:', err)
    }
  }

  const handleDelete = async (name: string) => {
    try {
      const res = await fetch(`http://localhost:8000/credentials/${name}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        setMessage("Credential deleted successfully!")
        fetchCredentials()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Failed to delete credential:', err)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your application configuration</p>
      </div>

      <Separator />

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Credentials</h2>
          <p className="text-sm text-muted-foreground">Manage device authentication credentials</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Credential
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
            <CardTitle>Add New Credential</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Credential Name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
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
                  type="password"
                  placeholder="Secret (Optional)"
                  value={formData.secret}
                  onChange={(e) => setFormData({...formData, secret: e.target.value})}
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
            <Key className="h-5 w-5" />
            Saved Credentials
          </CardTitle>
          <CardDescription>
            {Object.keys(credentials).length} credential(s) saved
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : Object.keys(credentials).length === 0 ? (
            <p className="text-sm text-muted-foreground">No credentials configured</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Username</TableHead>
                  <TableHead>Has Secret</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(credentials).map(([name, cred]) => (
                  <TableRow key={name}>
                    <TableCell className="font-medium">{name}</TableCell>
                    <TableCell>{cred.username}</TableCell>
                    <TableCell>
                      <Badge variant={cred.secret ? "default" : "secondary"}>
                        {cred.secret ? "Yes" : "No"}
                      </Badge>
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
