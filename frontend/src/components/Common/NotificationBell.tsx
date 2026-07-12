import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Bell } from "lucide-react"

import { AdminNotificationsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useI18n } from "@/contexts/i18n"

// Map the raw notification `type` code to a readable i18n label.
const TYPE_LABEL: Record<string, string> = {
  interview_scheduled: "notifications.type.interview_scheduled",
  interview_reminder: "notifications.type.interview_reminder",
  feedback_overdue: "notifications.type.feedback_overdue",
  batch_notify: "notifications.type.batch_notify",
}

export function NotificationBell() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  // List recent notifications (read + unread). Marking one as read keeps it
  // in the list, just restyled; only the bell's red dot goes away.
  const { data } = useQuery({
    queryKey: ["notifications"],
    queryFn: () =>
      AdminNotificationsService.listNotifications({
        unreadOnly: false,
        limit: 10,
      }),
  })
  const items = data?.data ?? []
  const hasUnread = items.some((n) => !n.read_status)

  const markAll = useMutation({
    mutationFn: () => AdminNotificationsService.markAllRead(),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  })

  // Clicking a notification marks it as read (stays visible, red dot clears).
  const markOne = useMutation({
    mutationFn: (notificationId: string) =>
      AdminNotificationsService.markRead({ notificationId }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  })

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="size-5" />
          {hasUnread && (
            <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-red-500" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>{t("notifications.title")}</span>
          {hasUnread && (
            <button
              type="button"
              className="text-xs underline"
              onClick={() => markAll.mutate()}
            >
              {t("notifications.markAllRead")}
            </button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {items.length === 0 ? (
          <DropdownMenuItem disabled>
            {t("notifications.allCaughtUp")}
          </DropdownMenuItem>
        ) : (
          items.map((n) => {
            const unreadItem = !n.read_status
            return (
              <DropdownMenuItem
                key={n.id}
                className="flex flex-col items-start"
                onSelect={() => unreadItem && markOne.mutate(n.id)}
              >
                <div className="flex items-center gap-1.5 w-full">
                  {unreadItem && (
                    <span className="size-1.5 rounded-full bg-red-500 shrink-0" />
                  )}
                  {TYPE_LABEL[n.type] && (
                    <span className="text-xs text-muted-foreground">
                      {t(TYPE_LABEL[n.type] as never)}
                    </span>
                  )}
                </div>
                <p
                  className={
                    unreadItem
                      ? "text-sm font-medium"
                      : "text-sm text-muted-foreground"
                  }
                >
                  {n.content}
                </p>
              </DropdownMenuItem>
            )
          })
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
