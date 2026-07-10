import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminInterviewsService,
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

export const Route = createFileRoute("/_layout/applications/$id")({
  component: ApplicationDetail,
  head: () => ({ meta: [{ title: "Application - ATS" }] }),
})

function ApplicationDetail() {
  const { id } = Route.useParams()
  const { t } = useI18n()

  const { data: app } = useQuery({
    queryKey: ["application", id],
    queryFn: () =>
      AdminApplicationsService.getApplication({ applicationId: id }),
  })
  const { data: candData } = useQuery({
    queryKey: ["candidates"],
    queryFn: () => AdminCandidatesService.listCandidates({}),
  })
  const { data: jobsData } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => AdminJobsService.listJobs({}),
  })
  const { data: ivData } = useQuery({
    queryKey: ["interviews"],
    queryFn: () => AdminInterviewsService.listInterviews({}),
  })

  const candidateMap = new Map(candData?.data?.map((c) => [c.id, c.name]))
  const jobMap = new Map(jobsData?.data?.map((j) => [j.id, j.title]))
  const interviews = ivData?.data?.filter((i) => i.application_id === id) ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          {candidateMap.get(app?.candidate_id || "") || t("common.application")}
        </h1>
        <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
          <span>
            {t("common.job")}: {jobMap.get(app?.job_id || "") || "-"}
          </span>
          <span>
            {t("common.stage")}:{" "}
            <Badge variant="secondary">
              {app ? t(STAGE_KEYS[app.stage] as never) : ""}
            </Badge>
          </span>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">{t("interviews.title")}</h2>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("interviews.round")}</TableHead>
                <TableHead>{t("interviews.scheduledTime")}</TableHead>
                <TableHead>{t("common.status")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {interviews.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground"
                  >
                    {t("interviews.noInterviews")}
                  </TableCell>
                </TableRow>
              ) : (
                interviews.map((iv) => (
                  <TableRow key={iv.id}>
                    <TableCell>{iv.round}</TableCell>
                    <TableCell>
                      {new Date(iv.scheduled_time).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {iv.status === "CANCELLED"
                          ? t("common.cancelled")
                          : iv.status}
                      </Badge>
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
