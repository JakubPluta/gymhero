import { Link } from '@tanstack/react-router'
import { ClipboardList, Dumbbell, ListChecks, type LucideIcon } from 'lucide-react'
import { useMe } from '@/auth/useAuth'
import { FadeIn } from '@/components/fade-in'
import { PageHeader } from '@/components/page-header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useExercises } from '@/features/exercises/hooks'
import { useTrainingPlans } from '@/features/training-plans/hooks'
import { useTrainingUnits } from '@/features/training-units/hooks'

type StatCardProps = {
  title: string
  value: number | undefined
  icon: LucideIcon
  to: '/exercises' | '/training-units' | '/training-plans'
  isLoading: boolean
}

function StatCard({ title, value, icon: Icon, to, isLoading }: StatCardProps) {
  return (
    <Link to={to} className="block">
      <Card className="transition-colors hover:border-primary/40">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <Icon className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-9 w-16" />
          ) : (
            <div className="text-3xl font-semibold tracking-tight">{value ?? 0}</div>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}

export function DashboardPage() {
  const { data: user } = useMe()
  // limit: 1 — we only need the `total` from each owner-scoped list.
  const exercises = useExercises({ scope: 'my', skip: 0, limit: 1 })
  const units = useTrainingUnits({ scope: 'my', skip: 0, limit: 1 })
  const plans = useTrainingPlans({ scope: 'my', skip: 0, limit: 1 })

  const greeting = user?.full_name ?? user?.email ?? 'there'

  return (
    <FadeIn className="space-y-6">
      <PageHeader
        title={`Welcome back, ${greeting}`}
        description="Your training library at a glance."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="My exercises"
          value={exercises.data?.total}
          icon={Dumbbell}
          to="/exercises"
          isLoading={exercises.isLoading}
        />
        <StatCard
          title="My training units"
          value={units.data?.total}
          icon={ListChecks}
          to="/training-units"
          isLoading={units.isLoading}
        />
        <StatCard
          title="My training plans"
          value={plans.data?.total}
          icon={ClipboardList}
          to="/training-plans"
          isLoading={plans.isLoading}
        />
      </div>
    </FadeIn>
  )
}
