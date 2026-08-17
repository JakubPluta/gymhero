import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'
import { getErrorMessage } from '@/api/errors'
import type { Exercise } from '@/api/types'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useBodyParts, useExerciseTypes, useLevels } from '@/features/reference/hooks'
import { useCreateExercise, useUpdateExercise } from './hooks'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  target_body_part_id: z.coerce.number().int().positive('Select a body part'),
  exercise_type_id: z.coerce.number().int().positive('Select a type'),
  level_id: z.coerce.number().int().positive('Select a level'),
})
type FormValues = z.infer<typeof schema>

function toFormValues(exercise?: Exercise): FormValues {
  return {
    name: exercise?.name ?? '',
    description: exercise?.description ?? '',
    target_body_part_id: exercise?.target_body_part?.id ?? 0,
    exercise_type_id: exercise?.exercise_type?.id ?? 0,
    level_id: exercise?.level?.id ?? 0,
  }
}

type ExerciseFormDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  exercise?: Exercise
}

export function ExerciseFormDialog({
  open,
  onOpenChange,
  exercise,
}: ExerciseFormDialogProps) {
  const isEdit = exercise !== undefined
  const bodyParts = useBodyParts()
  const types = useExerciseTypes()
  const levels = useLevels()
  const createExercise = useCreateExercise()
  const updateExercise = useUpdateExercise(exercise?.id ?? 0)

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: toFormValues(exercise),
  })

  useEffect(() => {
    if (open) form.reset(toFormValues(exercise))
  }, [open, exercise, form])

  const isPending = createExercise.isPending || updateExercise.isPending

  const onSubmit = (values: FormValues) => {
    const payload = {
      name: values.name,
      description: values.description?.trim() ? values.description.trim() : null,
      target_body_part_id: values.target_body_part_id,
      exercise_type_id: values.exercise_type_id,
      level_id: values.level_id,
    }
    const mutation = isEdit ? updateExercise : createExercise
    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success(isEdit ? 'Exercise updated' : 'Exercise created')
        onOpenChange(false)
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit exercise' : 'New exercise'}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? 'Update the details of your exercise.'
              : 'Add a new exercise to your library.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Bench press" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea rows={3} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid gap-4 sm:grid-cols-3">
              <FormField
                control={form.control}
                name="target_body_part_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Body part</FormLabel>
                    <Select
                      value={field.value ? String(field.value) : undefined}
                      onValueChange={(value) => field.onChange(Number(value))}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {bodyParts.data?.map((item) => (
                          <SelectItem key={item.id} value={String(item.id)}>
                            {item.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="exercise_type_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Type</FormLabel>
                    <Select
                      value={field.value ? String(field.value) : undefined}
                      onValueChange={(value) => field.onChange(Number(value))}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {types.data?.map((item) => (
                          <SelectItem key={item.id} value={String(item.id)}>
                            {item.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="level_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Level</FormLabel>
                    <Select
                      value={field.value ? String(field.value) : undefined}
                      onValueChange={(value) => field.onChange(Number(value))}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {levels.data?.map((item) => (
                          <SelectItem key={item.id} value={String(item.id)}>
                            {item.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
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
              <Button type="submit" disabled={isPending}>
                {isEdit ? 'Save changes' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
