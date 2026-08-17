import { Outlet, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { useMe } from '@/auth/useAuth'
import { ModeToggle } from '@/components/mode-toggle'
import { Separator } from '@/components/ui/separator'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from './app-sidebar'

export function AppLayout() {
  const navigate = useNavigate()
  const { isError } = useMe()

  useEffect(() => {
    // Session no longer valid (refresh failed / revoked) → back to login.
    if (isError) navigate({ to: '/login' })
  }, [isError, navigate])

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex flex-1 items-center justify-end">
            <ModeToggle />
          </div>
        </header>
        <main className="flex flex-1 flex-col gap-6 p-4 md:p-6">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
