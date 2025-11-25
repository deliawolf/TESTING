"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Plus, Edit, Trash2, X, Download, Upload } from "lucide-react"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

type Device = {
  name: string
  host: string
  device_type: string
  port: number
  username?: string
  password?: string
  secret?: string
  credential_name?: string
  jumphost_profile?: string
  jumphost2_profile?: string
  tags: string[]
}

export default function InventoryPage() {
  const [devices, setDevices] = useState<Record<string, any>>({})
  const [jumphosts, setJumphosts] = useState<Record<string, any>>({})
  const [credentials, setCredentials] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState("")
  const [editingDevice, setEditingDevice] = useState<string | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  
  const [formData, setFormData] = useState<Device>({
    name: "",
    host: "",
    device_type: "cisco_nxos",
    port: 22,
    credential_name: "",
    jumphost_profile: "",
    jumphost2_profile: "",
    tags: []
  })
  const [tagInput, setTagInput] = useState("")

  const fetchAll = async () => {
    try {
      const [devicesRes, jumphostsRes, credentialsRes] = await Promise.all([
        fetch('http://localhost:8000/inventory/devices'),
        fetch('http://localhost:8000/jumphosts'),
        fetch('http://localhost:8000/credentials')
      ])
      
      setDevices(await devicesRes.json())
      setJumphosts(await jumphostsRes.json())
      setCredentials(await credentialsRes.json())
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  const handleExportCSV = async () => {
    try {
      const res = await fetch('http://localhost:8000/inventory/export/csv')
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'inventory_export.csv'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        setMessage("Inventory exported successfully!")
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Export failed:', err)
      setMessage("Export failed")
      setTimeout(() => setMessage(""), 3000)
    }
  }

  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://localhost:8000/inventory/import/csv', {
        method: 'POST',
        body: formData
      })
      
      if (res.ok) {
        const result = await res.json()
        setMessage(result.message)
        fetchAll()
        setTimeout(() => setMessage(""), 5000)
      } else {
        const error = await res.json()
        setMessage(error.detail || "Import failed")
        setTimeout(() => setMessage(""), 5000)
      }
    } catch (err) {
      console.error('Import failed:', err)
      setMessage("Import failed")
      setTimeout(() => setMessage(""), 3000)
    }
    
    // Reset file input
    e.target.value = ''
  }

  const openAddForm = () => {
    setEditingDevice(null)
    setFormData({
      name: "",
      host: "",
      device_type: "cisco_nxos",
      port: 22,
      credential_name: "",
      jumphost_profile: "",
      jumphost2_profile: "",
      tags: []
    })
    setTagInput("")
    setSheetOpen(true)
  }

  const openEditForm = (deviceName: string) => {
    const device = devices[deviceName]
    setEditingDevice(deviceName)
    setFormData({
      name: deviceName,
      host: device.host,
      device_type: device.device_type,
      port: device.port,
      credential_name: device.credential_name || "",
      jumphost_profile: device.jumphost_profile || "",
      jumphost2_profile: device.jumphost2_profile || "",
      tags: device.tags || []
    })
    setTagInput("")
    setSheetOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const url = editingDevice 
      ? `http://localhost:8000/inventory/devices/${editingDevice}`
      : 'http://localhost:8000/inventory/devices'
    
    const method = editingDevice ? 'PUT' : 'POST'

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (res.ok) {
        setMessage(editingDevice ? "Device updated successfully!" : "Device added successfully!")
        setSheetOpen(false)
        fetchAll()
        setTimeout(() => setMessage(""), 3000)
      } else {
        const error = await res.json()
        setMessage(error.detail || "Operation failed")
        setTimeout(() => setMessage(""), 5000)
      }
    } catch (err) {
      setMessage("Failed to save device")
      setTimeout(() => setMessage(""), 3000)
    }
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`Delete device ${name}?`)) return
    
    try {
      const res = await fetch(`http://localhost:8000/inventory/devices/${name}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        setMessage("Device deleted successfully!")
        fetchAll()
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error('Failed to delete device:', err)
    }
  }

  const addTag = () => {
    if (tagInput && !formData.tags.includes(tagInput)) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput] })
      setTagInput("")
    }
  }

  const removeTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Inventory</h1>
          <p className="text-muted-foreground">Manage your network devices</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportCSV}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => document.getElementById('csv-upload')?.click()}>
            <Upload className="mr-2 h-4 w-4" />
            Import CSV
          </Button>
          <input
            id="csv-upload"
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={handleImportCSV}
          />
          <Button onClick={openAddForm}>
            <Plus className="mr-2 h-4 w-4" />
            Add Device
          </Button>
        </div>
      </div>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent className="w-[600px] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>{editingDevice ? 'Edit Device' : 'Add New Device'}</SheetTitle>
            <SheetDescription>
              {editingDevice ? 'Update device configuration' : 'Add a new device to your inventory'}
            </SheetDescription>
          </SheetHeader>

          <form onSubmit={handleSubmit} className="space-y-4 mt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="text-sm font-medium">Device Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  disabled={!!editingDevice}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Hostname/IP</label>
                <Input
                  value={formData.host}
                  onChange={(e) => setFormData({...formData, host: e.target.value})}
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Port</label>
                <Input
                  type="number"
                  value={formData.port}
                  onChange={(e) => setFormData({...formData, port: parseInt(e.target.value)})}
                  required
                />
              </div>

              <div className="col-span-2">
                <label className="text-sm font-medium">Device Type</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.device_type}
                  onChange={(e) => setFormData({...formData, device_type: e.target.value})}
                >
                  <option value="cisco_nxos">Cisco NX-OS</option>
                  <option value="cisco_ios">Cisco IOS</option>
                  <option value="cisco_xe">Cisco IOS-XE</option>
                  <option value="cisco_xr">Cisco IOS-XR</option>
                  <option value="arista_eos">Arista EOS</option>
                  <option value="juniper_junos">Juniper Junos</option>
                </select>
              </div>

              <div className="col-span-2">
                <label className="text-sm font-medium">Credential</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.credential_name}
                  onChange={(e) => setFormData({...formData, credential_name: e.target.value})}
                >
                  <option value="">Select credential...</option>
                  {Object.keys(credentials).map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Jump Host 1</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.jumphost_profile}
                  onChange={(e) => setFormData({...formData, jumphost_profile: e.target.value})}
                >
                  <option value="">None (Direct)</option>
                  {Object.keys(jumphosts).map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Jump Host 2</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.jumphost2_profile}
                  onChange={(e) => setFormData({...formData, jumphost2_profile: e.target.value})}
                >
                  <option value="">None</option>
                  {Object.keys(jumphosts).map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>

              <div className="col-span-2">
                <label className="text-sm font-medium">Tags</label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    placeholder="Add tag..."
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  />
                  <Button type="button" onClick={addTag} size="sm">Add</Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map(tag => (
                    <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                      {tag}
                      <X className="h-3 w-3 cursor-pointer" onClick={() => removeTag(tag)} />
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {editingDevice ? 'Update Device' : 'Add Device'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setSheetOpen(false)}>
                Cancel
              </Button>
            </div>
          </form>
        </SheetContent>
      </Sheet>

      <Card>
        <CardHeader>
          <CardTitle>Devices</CardTitle>
          <CardDescription>
            {Object.keys(devices).length} device(s) configured
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Credential</TableHead>
                  <TableHead>Tags</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(devices).map(([name, device]) => (
                  <TableRow key={name}>
                    <TableCell className="font-medium">{name}</TableCell>
                    <TableCell>{device.host}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{device.device_type}</Badge>
                    </TableCell>
                    <TableCell>{device.credential_name || '-'}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {device.tags?.map((tag: string) => (
                          <Badge key={tag} variant="outline">{tag}</Badge>
                        )) || '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => openEditForm(name)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDelete(name)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
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
