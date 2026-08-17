import {
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from '@tanstack/react-router'
import { hasSession } from '@/auth/store'
import { AppLayout } from '@/components/app-layout'
import { LoginPage } from '@/features/auth/login-page'
import { RegisterPage } from '@/features/auth/register-page'
import { DashboardPage } from '@/features/dashboard/dashboard-page'
import { ExerciseDetailPage } from '@/features/exercises/exercise-detail-page'
import { ExercisesPage } from '@/features/exercises/exercises-page'
import { TrainingPlanDetailPage } from '@/features/training-plans/training-plan-detail-page'
import { TrainingPlansPage } from '@/features/training-plans/training-plans-page'
import { TrainingUnitDetailPage } from '@/features/training-units/training-unit-detail-page'
import { TrainingUnitsPage } from '@/features/training-units/training-units-page'

const rootRoute = createRootRoute({ component: () => <Outlet /> })

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  beforeLoad: () => {
    if (hasSession()) throw redirect({ to: '/' })
  },
  component: LoginPage,
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  beforeLoad: () => {
    if (hasSession()) throw redirect({ to: '/' })
  },
  component: RegisterPage,
})

// Pathless layout route: guards the whole app and renders the sidebar shell.
const appLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'app',
  beforeLoad: () => {
    if (!hasSession()) throw redirect({ to: '/login' })
  },
  component: AppLayout,
})

const dashboardRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/',
  component: DashboardPage,
})

const exercisesRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/exercises',
  component: ExercisesPage,
})

const exerciseDetailRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/exercises/$exerciseId',
  component: ExerciseDetailRoute,
})
function ExerciseDetailRoute() {
  const { exerciseId } = exerciseDetailRoute.useParams()
  return <ExerciseDetailPage id={Number(exerciseId)} />
}

const trainingUnitsRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/training-units',
  component: TrainingUnitsPage,
})

const trainingUnitDetailRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/training-units/$unitId',
  component: TrainingUnitDetailRoute,
})
function TrainingUnitDetailRoute() {
  const { unitId } = trainingUnitDetailRoute.useParams()
  return <TrainingUnitDetailPage id={Number(unitId)} />
}

const trainingPlansRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/training-plans',
  component: TrainingPlansPage,
})

const trainingPlanDetailRoute = createRoute({
  getParentRoute: () => appLayoutRoute,
  path: '/training-plans/$planId',
  component: TrainingPlanDetailRoute,
})
function TrainingPlanDetailRoute() {
  const { planId } = trainingPlanDetailRoute.useParams()
  return <TrainingPlanDetailPage id={Number(planId)} />
}

const routeTree = rootRoute.addChildren([
  loginRoute,
  registerRoute,
  appLayoutRoute.addChildren([
    dashboardRoute,
    exercisesRoute,
    exerciseDetailRoute,
    trainingUnitsRoute,
    trainingUnitDetailRoute,
    trainingPlansRoute,
    trainingPlanDetailRoute,
  ]),
])

export const router = createRouter({ routeTree, defaultPreload: 'intent' })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
