import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"

import { PortalJobsService } from "@/client"
import { useI18n } from "@/contexts/i18n"

export const Route = createFileRoute("/portal/")({
  component: PortalJobsList,
  head: () => ({ meta: [{ title: "Open Positions - ATS" }] }),
})

function PortalJobsList() {
  const { t } = useI18n()
  const { data, isLoading } = useQuery({
    queryKey: ["portal-jobs"],
    queryFn: () => PortalJobsService.listPortalJobs({}),
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{t("portal.jobsTitle")}</h1>
      {isLoading ? (
        <p className="text-muted-foreground">{t("common.loading")}</p>
      ) : (data?.data ?? []).length === 0 ? (
        <p className="text-muted-foreground">{t("portal.noJobs")}</p>
      ) : (
        <div className="space-y-3">
          {data?.data?.map((j) => (
            <Link
              key={j.id}
              to="/portal/jobs/$id"
              params={{ id: j.id }}
              className="block rounded-lg border p-4 hover:bg-accent transition-colors"
            >
              <h2 className="font-semibold">{j.title}</h2>
              <p className="text-sm text-muted-foreground">
                {j.location || "Remote"} · {j.headcount} {t("portal.openings")}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
