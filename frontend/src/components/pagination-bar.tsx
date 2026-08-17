import { Button } from '@/components/ui/button'

type PaginationBarProps = {
  skip: number
  limit: number
  total: number
  onSkipChange: (skip: number) => void
}

export function PaginationBar({
  skip,
  limit,
  total,
  onSkipChange,
}: PaginationBarProps) {
  const from = total === 0 ? 0 : skip + 1
  const to = Math.min(skip + limit, total)
  const canPrev = skip > 0
  const canNext = skip + limit < total
  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">
        {from}–{to} of {total}
      </p>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!canPrev}
          onClick={() => onSkipChange(Math.max(0, skip - limit))}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!canNext}
          onClick={() => onSkipChange(skip + limit)}
        >
          Next
        </Button>
      </div>
    </div>
  )
}
