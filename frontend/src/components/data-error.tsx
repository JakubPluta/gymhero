import { AlertCircle } from 'lucide-react'
import { getErrorMessage } from '@/api/errors'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export function DataError({ error }: { error: unknown }) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Something went wrong</AlertTitle>
      <AlertDescription>{getErrorMessage(error)}</AlertDescription>
    </Alert>
  )
}
