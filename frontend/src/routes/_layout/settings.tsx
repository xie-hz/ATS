import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { AdminUsersService } from "@/client"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import { useI18n } from "@/contexts/i18n"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const profileSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }),
  email: z.email({ message: "Invalid email" }),
})
type ProfileData = z.infer<typeof profileSchema>

const passwordSchema = z.object({
  current_password: z.string().min(8, { message: "At least 8 characters" }),
  new_password: z.string().min(8, { message: "At least 8 characters" }),
})
type PasswordData = z.infer<typeof passwordSchema>

export const Route = createFileRoute("/_layout/settings")({
  component: SettingsPage,
  head: () => ({ meta: [{ title: "Settings - ATS" }] }),
})

function SettingsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()

  const profileForm = useForm<ProfileData>({
    resolver: zodResolver(profileSchema),
    defaultValues: { name: user?.name || "", email: user?.email || "" },
  })

  const passwordForm = useForm<PasswordData>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { current_password: "", new_password: "" },
  })

  const profileMutation = useMutation({
    mutationFn: (data: ProfileData) =>
      AdminUsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(t("settings.saveProfile"))
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const passwordMutation = useMutation({
    mutationFn: (data: PasswordData) =>
      AdminUsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(t("settings.updatePassword"))
      passwordForm.reset()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="space-y-8 max-w-xl">
      <h1 className="text-2xl font-bold">{t("settings.title")}</h1>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">{t("settings.profile")}</h2>
        <Form {...profileForm}>
          <form
            onSubmit={profileForm.handleSubmit((d) =>
              profileMutation.mutate(d),
            )}
            className="space-y-4"
          >
            <FormField
              control={profileForm.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("candidates.name")}</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />
            <FormField
              control={profileForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("candidates.email")}</FormLabel>
                  <FormControl>
                    <Input type="email" {...field} />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />
            <LoadingButton type="submit" loading={profileMutation.isPending}>
              {t("settings.saveProfile")}
            </LoadingButton>
          </form>
        </Form>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">
          {t("settings.changePassword")}
        </h2>
        <Form {...passwordForm}>
          <form
            onSubmit={passwordForm.handleSubmit((d) =>
              passwordMutation.mutate(d),
            )}
            className="space-y-4"
          >
            <FormField
              control={passwordForm.control}
              name="current_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("settings.currentPassword")}</FormLabel>
                  <FormControl>
                    <PasswordInput {...field} />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />
            <FormField
              control={passwordForm.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("settings.newPassword")}</FormLabel>
                  <FormControl>
                    <PasswordInput {...field} />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />
            <LoadingButton type="submit" loading={passwordMutation.isPending}>
              {t("settings.updatePassword")}
            </LoadingButton>
          </form>
        </Form>
      </div>
    </div>
  )
}
