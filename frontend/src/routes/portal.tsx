import { createFileRoute, Link, Outlet } from "@tanstack/react-router"

import { useI18n } from "@/contexts/i18n"

export const Route = createFileRoute("/portal")({
  component: PortalLayout,
})

function PortalLayout() {
  const { t } = useI18n()
  return (
    <div className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="mx-auto max-w-4xl flex items-center justify-between px-4 h-14">
          <Link to="/portal" className="font-bold">
            ATS Jobs
          </Link>
          <nav className="flex gap-4 text-sm">
            <Link to="/portal" className="hover:underline">
              {t("nav.jobs")}
            </Link>
            <Link to="/portal/login" className="hover:underline">
              {t("portal.signIn")}
            </Link>
            <Link to="/portal/applications" className="hover:underline">
              {t("portal.myApplications")}
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-4xl p-4">
        <Outlet />
      </main>
    </div>
  )
}
