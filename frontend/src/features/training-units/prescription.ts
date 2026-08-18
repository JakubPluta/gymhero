import type { PrescribedSet, TrainingUnitExercise } from '@/api/types'

// One set as "12×80" (reps × weight), or a partial ("12", "@80"), or "?" if blank.
function formatSet(set: PrescribedSet): string {
  const { reps, weight } = set
  if (reps != null && weight != null) return `${reps}×${weight}`
  if (reps != null) return `${reps}`
  if (weight != null) return `@${weight}`
  return '?'
}

// Whole prescription: "12×80, 10×90, 10×90, 8×100", or "—" when there are no sets.
export function formatPrescription(link: TrainingUnitExercise): string {
  const sets = link.sets ?? []
  return sets.length > 0 ? sets.map(formatSet).join(', ') : '—'
}
