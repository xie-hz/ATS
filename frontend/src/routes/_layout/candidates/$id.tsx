import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminJobsService,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/candidates/$id")({
  component: CandidateDetail,
  head: () => ({ meta: [{ title: "Candidate - ATS" }] }),
})

function CandidateDetail() {
  const { id } = Route.useParams()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: candidate } = useQuery({
    queryKey: ["candidate", id],
    queryFn: () => AdminCandidatesService.getCandidate({ candidateId: id }),
  })
  const { data: appsData } = useQuery({
    queryKey: ["applications"],
    queryFn: () => AdminApplicationsService.listApplications({}),
  })
  const { data: jobsData } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => AdminJobsService.listJobs({}),
  })

  const jobMap = new Map(jobsData?.data?.map((j) => [j.id, j.title]))
  const apps = appsData?.data?.filter((a) => a.candidate_id === id) ?? []

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      AdminCandidatesService.uploadResume({
        candidateId: id,
        formData: { file: file as unknown as string },
      }),
    onSuccess: () => {
      showSuccessToast("Resume uploaded")
      queryClient.invalidateQueries({ queryKey: ["candidate", id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{candidate?.name}</h1>
          <p className="text-muted-foreground">{candidate?.email}</p>
        </div>
        <div>
          <input
            type="file"
            id="resume"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) uploadMutation.mutate(f)
            }}
          />
          <Button asChild>
            <label htmlFor="resume" className="cursor-pointer">
              {uploadMutation.isPending ? "Uploading..." : "Upload Resume"}
            </label>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-muted-foreground">Phone</p>
          <p>{candidate?.phone || "-"}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Source</p>
          <p>{candidate?.source || "-"}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Resume</p>
          {candidate?.resume_url ? (
            <a
              className="underline"
              href={candidate.resume_url}
              target="_blank"
              rel="noreferrer"
            >
              View
            </a>
          ) : (
            <p>-</p>
          )}
        </div>
        <div>
          <p className="text-muted-foreground">Tags</p>
          <div className="flex flex-wrap gap-1">
            {candidate?.tags?.map((t) => (
              <Badge key={t} variant="secondary" className="text-xs">
                {t}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Applications</h2>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Job</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {apps.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground"
                  >
                    No applications.
                  </TableCell>
                </TableRow>
              ) : (
                apps.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{jobMap.get(a.job_id) || "-"}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{a.stage}</Badge>
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
