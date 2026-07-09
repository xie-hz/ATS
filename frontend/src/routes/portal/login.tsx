import { useMutation } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"

import { PortalAuthService } from "@/client"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/portal/login")({
  component: PortalLogin,
  head: () => ({ meta: [{ title: "Sign In - ATS" }] }),
})

function PortalLogin() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [email, setEmail] = useState("")
  const [code, setCode] = useState("")
  const [sent, setSent] = useState(false)

  const sendMutation = useMutation({
    mutationFn: () => PortalAuthService.sendCode({ requestBody: { email } }),
    onSuccess: () => {
      showSuccessToast(t("portal.codeSent"))
      setSent(true)
    },
    onError: handleError.bind(showErrorToast),
  })

  const verifyMutation = useMutation({
    mutationFn: () =>
      PortalAuthService.verifyCode({ requestBody: { email, code } }),
    onSuccess: (res) => {
      localStorage.setItem("portal_token", res.access_token)
      navigate({ to: "/portal/applications" })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="max-w-md mx-auto space-y-6">
      <h1 className="text-2xl font-bold">{t("portal.loginTitle")}</h1>
      <p className="text-sm text-muted-foreground">{t("portal.loginHint")}</p>

      <div className="space-y-4">
        <div className="space-y-1.5">
          <Label>{t("login.email")}</Label>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={sent}
            placeholder="you@example.com"
          />
        </div>

        {!sent ? (
          <LoadingButton
            loading={sendMutation.isPending}
            onClick={() => sendMutation.mutate()}
            className="w-full"
            disabled={!email}
          >
            {t("portal.sendCode")}
          </LoadingButton>
        ) : (
          <>
            <div className="space-y-1.5">
              <Label>{t("portal.verificationCode")}</Label>
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={t("portal.codePlaceholder")}
              />
            </div>
            <LoadingButton
              loading={verifyMutation.isPending}
              onClick={() => verifyMutation.mutate()}
              className="w-full"
              disabled={!code}
            >
              {t("portal.signIn")}
            </LoadingButton>
            <button
              type="button"
              className="text-sm text-muted-foreground underline"
              onClick={() => {
                setSent(false)
                setCode("")
              }}
            >
              {t("portal.useDifferentEmail")}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
