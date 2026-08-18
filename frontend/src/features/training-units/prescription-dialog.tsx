import { Plus, X } from 'lucide-react'
import { useRef, useState } from 'react'
import type { PrescribedSet, PrescriptionUpdate } from '@/api/types'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'

// Fields stay strings (native number inputs emit strings); blank means "not set".
type Row = { key: number; reps: string; weight: string }

type PrescriptionDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  exerciseName: string
  initialSets: PrescribedSet[]
  isPending: boolean
  onSubmit: (prescription: PrescriptionUpdate) => void
}

const parse = (raw: string): number | null => (raw.trim() === '' ? null : Number(raw))

// A field is valid when blank or a non-negative number.
const fieldValid = (raw: string): boolean => {
  if (raw.trim() === '') return true
  const n = Number(raw)
  return !Number.isNaN(n) && n >= 0
}

const toRows = (sets: PrescribedSet[]): Row[] => {
  const source = sets.length > 0 ? sets : [{ reps: null, weight: null }]
  return source.map((set, index) => ({
    key: index,
    reps: set.reps?.toString() ?? '',
    weight: set.weight?.toString() ?? '',
  }))
}

// Presentational per-set editor. The parent (fresh-mounts this per edit) owns the
// mutation and closing; a blank row is dropped on save, list order = set order.
export function PrescriptionDialog({
  open,
  onOpenChange,
  exerciseName,
  initialSets,
  isPending,
  onSubmit,
}: PrescriptionDialogProps) {
  const [rows, setRows] = useState<Row[]>(() => toRows(initialSets))
  const nextKey = useRef(rows.length)

  const setRow = (key: number, field: 'reps' | 'weight', value: string) =>
    setRows((current) =>
      current.map((row) => (row.key === key ? { ...row, [field]: value } : row)),
    )
  const addRow = () =>
    setRows((current) => [...current, { key: nextKey.current++, reps: '', weight: '' }])
  const removeRow = (key: number) =>
    setRows((current) => current.filter((row) => row.key !== key))

  const hasInvalid = rows.some((r) => !fieldValid(r.reps) || !fieldValid(r.weight))

  const handleSave = () => {
    const sets = rows
      .filter((r) => r.reps.trim() !== '' || r.weight.trim() !== '')
      .map((r) => ({ reps: parse(r.reps), weight: parse(r.weight) }))
    onSubmit({ sets })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Prescription</DialogTitle>
          <DialogDescription>
            Sets for {exerciseName} — one row per set (reps × weight in kg).
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <div className="grid grid-cols-[1.5rem_1fr_1fr_2rem] items-center gap-2 text-xs text-muted-foreground">
            <span>#</span>
            <span>Reps</span>
            <span>Weight</span>
            <span />
          </div>
          {rows.map((row, index) => (
            <div
              key={row.key}
              className="grid grid-cols-[1.5rem_1fr_1fr_2rem] items-center gap-2"
            >
              <span className="text-sm text-muted-foreground">{index + 1}</span>
              <Input
                type="number"
                min="0"
                step="1"
                placeholder="—"
                value={row.reps}
                onChange={(e) => setRow(row.key, 'reps', e.target.value)}
              />
              <Input
                type="number"
                min="0"
                step="0.5"
                placeholder="—"
                value={row.weight}
                onChange={(e) => setRow(row.key, 'weight', e.target.value)}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                aria-label={`Remove set ${index + 1}`}
                onClick={() => removeRow(row.key)}
              >
                <X className="size-4" />
              </Button>
            </div>
          ))}
          <Button type="button" variant="outline" size="sm" onClick={addRow}>
            <Plus className="mr-2 size-4" />
            Add set
          </Button>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isPending}
          >
            Cancel
          </Button>
          <Button type="button" onClick={handleSave} disabled={isPending || hasInvalid}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
