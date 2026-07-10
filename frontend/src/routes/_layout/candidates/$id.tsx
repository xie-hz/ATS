import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminJobsService,
  type ApplicationStage,
  OpenAPI,
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
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const STAGE_KEYS: Record<ApplicationStage, string> = {
  APPLIED: "board.applied",
  SCREENING: "board.screening",
  INTERVIEW: "board.interview",
  OFFER: "board.offer",
  HIRED: "board.hired",
  REJECTED: "board.rejected",
}

export const Route = createFileRoute("/_layout/candidates/$id")({
  component: CandidateDetail,
  head: () => ({ meta: [{ title: "Candidate - ATS" }] }),
})

function CandidateDetail() {
  const { id } = Route.useParams()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()

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
      showSuccessToast(t("candidates.resumeUploaded"))
      queryClient.invalidateQueries({ queryKey: ["candidate", id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  // Resolve the resume storage key to a fresh, directly-openable URL
  // (local path or a 1h MinIO presigned URL) and open it in a new tab.
  const viewResume = async () => {
    try {
      const res = await AdminCandidatesService.downloadResume({
        candidateId: id,
      })
      const url = (res as { url: string }).url
      // Local backend returns a relative "/uploads/..." path on the API origin;
      // MinIO returns an absolute presigned URL. Prefix relative URLs only.
      const full = url.startsWith("http") ? url : `${OpenAPI.BASE}${url}`
      window.open(full, "_blank", "noreferrer")
    } catch (e) {
      handleError.call(showErrorToast, e as never)
    }
  }

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
              {uploadMutation.isPending
                ? t("candidates.uploading")
                : t("candidates.uploadResume")}
            </label>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-muted-foreground">{t("candidates.phone")}</p>
          <p>{candidate?.phone || "-"}</p>
        </div>
        <div>
          <p className="text-muted-foreground">{t("candidates.source")}</p>
          <p>{candidate?.source || "-"}</p>
        </div>
        <div>
          <p className="text-muted-foreground">{t("candidates.resume")}</p>
          {candidate?.resume_url ? (
            <button
              type="button"
              className="underline text-sm"
              onClick={viewResume}
            >
              {t("common.view")}
            </button>
          ) : (
            <p>-</p>
          )}
        </div>
        <div>
          <p className="text-muted-foreground">{t("candidates.tags")}</p>
          <div className="flex flex-wrap gap-1">
            {candidate?.tags?.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("candidates.applications")}
        </h2>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("common.job")}</TableHead>
                <TableHead>{t("common.stage")}</TableHead>
                <TableHead>{t("common.created")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {apps.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground"
                  >
                    {t("candidates.noApplications")}
                  </TableCell>
                </TableRow>
              ) : (
                apps.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{jobMap.get(a.job_id) || "-"}</TableCell>
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
