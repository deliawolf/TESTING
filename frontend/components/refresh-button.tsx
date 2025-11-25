"use client"

import { RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export function RefreshButton() {
  const [spinning, setSpinning] = useState(false)

  const handleRefresh = () => {
    setSpinning(true)
    window.location.reload()
  }

  return (
    <Button 
      variant="ghost" 
      size="sm"
      onClick={handleRefresh}
      disabled={spinning}
    >
      <RefreshCw className={`h-4 w-4 ${spinning ? 'animate-spin' : ''}`} />
    </Button>
  )
}
