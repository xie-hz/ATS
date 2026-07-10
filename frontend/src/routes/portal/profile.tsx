import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link, redirect } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import { PortalProfileService } from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/portal/profile")({
  component: PortalProfile,
  beforeLoad: () => {
    if (!localStorage.getItem("portal_token")) {
      throw redirect({ to: "/portal/login" })
    }
  },
  head: () => ({ meta: [{ title: "My Profile - ATS" }] }),
})

function PortalProfile() {
  const { t } = useI18n()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const { data: profile, isError } = useQuery({
    queryKey: ["portal-me"],
    queryFn: () => PortalProfileService.getMyProfile(),
  })

  const [name, setName] = useState("")
  const [phone, setPhone] = useState("")

  useEffect(() => {
    if (profile) {
      setName(profile.name ?? "")
      setPhone(profile.phone ?? "")
    }
  }, [profile])

  const saveMutation = useMutation({
    mutationFn: () =>
      PortalProfileService.updateMyProfile({
        requestBody: { name, phone },
      }),
    onSuccess: () => {
      showSuccessToast(t("portal.profileSaved"))
      queryClient.invalidateQueries({ queryKey: ["portal-me"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  // No candidate record yet (logged in but never applied).
  if (isError) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">{t("portal.profileTitle")}</h1>
        <p className="text-muted-foreground">{t("portal.noProfileYet")}</p>
        <Button asChild>
          <Link to="/portal">{t("nav.jobs")}</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("portal.profileTitle")}</h1>
      <div className="rounded-lg border p-6 space-y-4 max-w-md">
        <div className="space-y-1.5">
          <Label>{t("candidates.name")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>{t("candidates.email")}</Label>
          <Input value={profile?.email ?? ""} disabled />
        </div>
        <div className="space-y-1.5">
          <Label>{t("candidates.phone")}</Label>
          <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <LoadingButton
          loading={saveMutation.isPending}
          onClick={() => saveMutation.mutate()}
          className="w-full"
          disabled={!name}
        >
          {t("common.save")}
        </LoadingButton>
      </div>
    </div>
  )
}
