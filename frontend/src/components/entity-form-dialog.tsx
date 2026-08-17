import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
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
import { Textarea } from '@/components/ui/textarea'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

export type NameDescriptionPayload = { name: string; description: string | null }

type EntityFormDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  namePlaceholder: string
  submitLabel: string
  initialName: string
  initialDescription: string
  isPending: boolean
  onSubmit: (payload: NameDescriptionPayload) => void
}

// Presentational name + description form shared by the entities whose create/edit
// forms are identical (training units and plans). The parent owns the mutation,
// toasts, and closing via onSubmit's callbacks.
export function EntityFormDialog({
  open,
  onOpenChange,
  title,
  description,
  namePlaceholder,
  submitLabel,
  initialName,
  initialDescription,
  isPending,
  onSubmit,
}: EntityFormDialogProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', description: '' },
  })

  useEffect(() => {
    if (open) form.reset({ name: initialName, description: initialDescription })
  }, [open, initialName, initialDescription, form])

  const handleSubmit = (values: FormValues) => {
    onSubmit({
      name: values.name,
      description: values.description?.trim() ? values.description.trim() : null,
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder={namePlaceholder} {...field} />
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
                {submitLabel}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
