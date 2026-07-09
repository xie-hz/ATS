import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminInterviewsService,
  AdminJobsService,
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

export const Route = createFileRoute("/_layout/applications/$id")({
  component: ApplicationDetail,
  head: () => ({ meta: [{ title: "Application - ATS" }] }),
})

function ApplicationDetail() {
  const { id } = Route.useParams()

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
          {candidateMap.get(app?.candidate_id || "") || "Application"}
        </h1>
        <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
          <span>Job: {jobMap.get(app?.job_id || "") || "-"}</span>
          <span>
            Stage: <Badge variant="secondary">{app?.stage}</Badge>
          </span>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Interviews</h2>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Round</TableHead>
                <TableHead>Scheduled</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {interviews.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground"
                  >
                    No interviews yet.
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
                      <Badge variant="secondary">{iv.status}</Badge>
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
