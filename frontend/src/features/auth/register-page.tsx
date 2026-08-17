import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'
import { getErrorMessage } from '@/api/errors'
import { useRegister } from '@/auth/useAuth'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { AuthShell } from './auth-shell'

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  full_name: z.string().max(255).optional(),
  password: z.string().min(8, 'At least 8 characters').max(72),
})
type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const navigate = useNavigate()
  const register = useRegister()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', full_name: '', password: '' },
  })

  const onSubmit = (values: FormValues) => {
    const full_name = values.full_name?.trim() ? values.full_name.trim() : undefined
    register.mutate(
      { email: values.email, password: values.password, full_name },
      {
        onSuccess: () => {
          toast.success('Account created — sign in to continue')
          navigate({ to: '/login' })
        },
        onError: (error) => toast.error(getErrorMessage(error, 'Registration failed')),
      },
    )
  }

  return (
    <AuthShell
      title="Create your account"
      description="Start building your training plans"
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="you@example.com"
                    autoComplete="email"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="full_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Full name (optional)</FormLabel>
                <FormControl>
                  <Input autoComplete="name" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" autoComplete="new-password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={register.isPending}>
            {register.isPending ? 'Creating…' : 'Create account'}
          </Button>
        </form>
      </Form>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link
          to="/login"
          className="font-medium text-foreground underline-offset-4 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </AuthShell>
  )
}
