import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { PortalApplicationsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { useI18n } from "@/contexts/i18n"

export const Route = createFileRoute("/portal/applications")({
  component: PortalMyApplications,
  beforeLoad: () => {
    if (!localStorage.getItem("portal_token")) {
      throw redirect({ to: "/portal/login" })
    }
  },
  head: () => ({ meta: [{ title: "My Applications - ATS" }] }),
})

function PortalMyApplications() {
  const { t } = useI18n()
  const { data, isLoading } = useQuery({
    queryKey: ["portal-my-applications"],
    queryFn: () => PortalApplicationsService.listMyApplications(),
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{t("portal.myApplications")}</h1>
      {isLoading ? (
        <p className="text-muted-foreground">{t("common.loading")}</p>
      ) : (data ?? []).length === 0 ? (
        <p className="text-muted-foreground">{t("portal.noApplications")}</p>
      ) : (
        <div className="space-y-3">
          {data?.map((a) => (
            <div key={a.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{a.job_title}</h2>
                <Badge variant="secondary">{a.stage}</Badge>
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                {t("portal.applied")}{" "}
                {new Date(a.created_at || "").toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
