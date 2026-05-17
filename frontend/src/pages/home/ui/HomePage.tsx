import { useState } from 'react'
import { Button } from '@/shared/ui/button'

export function HomePage() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex flex-col items-center justify-center min-h-svh gap-4 p-8">
      <h1 className="text-4xl font-bold tracking-tight">Get started</h1>
      <p className="text-muted-foreground">
        Edit <code className="bg-muted px-1.5 py-0.5 rounded text-sm">src/App.tsx</code> and save to test HMR
      </p>
      <Button onClick={() => setCount((c) => c + 1)}>
        Count is {count}
      </Button>
    </div>
  )
}
