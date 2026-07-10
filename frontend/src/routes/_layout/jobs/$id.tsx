import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminJobsService,
  type ApplicationStage,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useI18n } from "@/contexts/i18n"

const STAGE_KEYS: Record<ApplicationStage, string> = {
  APPLIED: "board.applied",
  SCREENING: "board.screening",
  INTERVIEW: "board.interview",
  OFFER: "board.offer",
  HIRED: "board.hired",
  REJECTED: "board.rejected",
}

export const Route = createFileRoute("/_layout/jobs/$id")({
  component: JobDetail,
  head: () => ({ meta: [{ title: "Job - ATS" }] }),
})

function JobDetail() {
  const { id } = Route.useParams()
  const { t } = useI18n()

  const { data: job } = useQuery({
    queryKey: ["job", id],
    queryFn: () => AdminJobsService.getJob({ jobId: id }),
  })
  const { data: appsData } = useQuery({
    queryKey: ["applications"],
    queryFn: () => AdminApplicationsService.listApplications({ jobId: id }),
  })
  const { data: candData } = useQuery({
    queryKey: ["candidates"],
    queryFn: () => AdminCandidatesService.listCandidates({}),
  })

  const candidateMap = new Map(candData?.data?.map((c) => [c.id, c.name]))
  const apps = appsData?.data ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{job?.title}</h1>
        <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
          <span>
            {t("common.status")}:{" "}
            <Badge variant="secondary">{job?.status}</Badge>
          </span>
          <span>
            {t("jobs.headcount")}: {job?.headcount}
          </span>
          <span>
            {t("jobs.location")}: {job?.location || "-"}
          </span>
        </div>
      </div>

      {job?.description && (
        <div>
          <h2 className="text-lg font-semibold mb-2">
            {t("jobs.description")}
          </h2>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {job.description}
          </p>
        </div>
      )}
      {job?.requirements && (
        <div>
          <h2 className="text-lg font-semibold mb-2">
            {t("jobs.requirements")}
          </h2>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {job.requirements}
          </p>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("jobs.applicants", { n: apps.length })}
        </h2>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("common.candidate")}</TableHead>
                <TableHead>{t("common.stage")}</TableHead>
                <TableHead>{t("common.applied")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {apps.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground"
                  >
                    {t("jobs.noApplicants")}
                  </TableCell>
                </TableRow>
              ) : (
                apps.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">
                      {candidateMap.get(a.candidate_id) || "-"}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {t(STAGE_KEYS[a.stage] as never)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(a.created_at || "").toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  )
}
