import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PortalApplicationsService, PortalJobsService } from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/portal/jobs/$id")({
  component: PortalJobDetail,
  head: () => ({ meta: [{ title: "Job - ATS" }] }),
})

function PortalJobDetail() {
  const { id } = Route.useParams()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const { data: job } = useQuery({
    queryKey: ["portal-job", id],
    queryFn: () => PortalJobsService.getPortalJob({ jobId: id }),
  })

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [submitted, setSubmitted] = useState(false)

  const mutation = useMutation({
    mutationFn: () =>
      PortalApplicationsService.submitApplication({
        requestBody: { job_id: id, name, email, phone },
      }),
    onSuccess: () => {
      showSuccessToast(t("portal.submitApplication"))
      setSubmitted(true)
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{job?.title}</h1>
        <p className="text-sm text-muted-foreground">
          {job?.location || "Remote"} · {job?.headcount} {t("portal.openings")}
        </p>
      </div>

      {job?.description && (
        <div>
          <h2 className="font-semibold mb-1">{t("jobs.description")}</h2>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {job.description}
          </p>
        </div>
      )}
      {job?.requirements && (
        <div>
          <h2 className="font-semibold mb-1">{t("jobs.requirements")}</h2>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {job.requirements}
          </p>
        </div>
      )}

      {submitted ? (
        <div className="rounded-lg border p-6 text-center space-y-3">
          <p className="font-medium">{t("portal.applicationSubmitted")}</p>
          <p className="text-sm text-muted-foreground">
            {t("portal.trackHint")}
          </p>
          <Button asChild>
            <a href="/portal/login">{t("portal.signInToTrack")}</a>
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border p-6 space-y-4 max-w-md">
          <h2 className="font-semibold">{t("portal.apply")}</h2>
          <div className="space-y-1.5">
            <Label>{t("candidates.name")}</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>{t("candidates.email")}</Label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>{t("candidates.phone")}</Label>
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
          <LoadingButton
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
            className="w-full"
            disabled={!name || !email}
          >
            {t("portal.submitApplication")}
          </LoadingButton>
        </div>
      )}
    </div>
  )
}
