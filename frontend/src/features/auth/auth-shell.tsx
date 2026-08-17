import { Dumbbell } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

type AuthShellProps = {
  title: string
  description?: string
  children: React.ReactNode
}

export function AuthShell({ title, description, children }: AuthShellProps) {
  return (
    <div className="flex min-h-svh items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="flex size-11 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Dumbbell className="size-6" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          {description ? (
            <p className="text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
        <Card>
          <CardContent>{children}</CardContent>
        </Card>
      </div>
    </div>
  )
}
