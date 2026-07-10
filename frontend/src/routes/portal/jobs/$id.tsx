import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import {
  PortalApplicationsService,
  PortalJobsService,
  PortalProfileService,
} from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { useI18n } from "@/contexts/i18n"
import { usePortalAuth } from "@/contexts/portal-auth"
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
  const { isAuthenticated, email: authEmail } = usePortalAuth()
  const { data: job } = useQuery({
    queryKey: ["portal-job", id],
    queryFn: () => PortalJobsService.getPortalJob({ jobId: id }),
  })

  // When logged in, pre-fill name/phone from the candidate's saved profile.
  const { data: profile } = useQuery({
    queryKey: ["portal-me"],
    queryFn: () => PortalProfileService.getMyProfile(),
    enabled: isAuthenticated,
  })

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    if (profile) {
      setName(profile.name ?? "")
      setPhone(profile.phone ?? "")
    }
  }, [profile])

  const mutation = useMutation({
    mutationFn: () =>
      PortalApplicationsService.submitApplication({
        requestBody: {
          job_id: id,
          name,
          // Email is the login identity: read-only when logged in.
          email: isAuthenticated ? (authEmail ?? email) : email,
          phone,
        },
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
          {isAuthenticated ? (
            <Button asChild>
              <Link to="/portal/applications">
                {t("portal.myApplications")}
              </Link>
            </Button>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                {t("portal.trackHint")}
              </p>
              <Button asChild>
                <Link to="/portal/login">{t("portal.signInToTrack")}</Link>
              </Button>
            </>
          )}
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
              value={isAuthenticated ? (authEmail ?? "") : email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isAuthenticated}
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
            disabled={!name || (!isAuthenticated && !email)}
          >
            {t("portal.submitApplication")}
          </LoadingButton>
        </div>
      )}
    </div>
  )
}
