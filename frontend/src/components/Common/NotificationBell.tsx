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

export function NotificationBell() {
  const queryClient = useQueryClient()
  const { data } = useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: () =>
      AdminNotificationsService.listNotifications({
        unreadOnly: true,
        limit: 10,
      }),
  })
  const unread = data?.data ?? []

  const markAll = useMutation({
    mutationFn: () => AdminNotificationsService.markAllRead(),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  })

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="size-5" />
          {unread.length > 0 && (
            <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-red-500" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notifications</span>
          {unread.length > 0 && (
            <button
              type="button"
              className="text-xs underline"
              onClick={() => markAll.mutate()}
            >
              Mark all read
            </button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {unread.length === 0 ? (
          <DropdownMenuItem disabled>
            You&apos;re all caught up
          </DropdownMenuItem>
        ) : (
          unread.map((n) => (
            <DropdownMenuItem key={n.id} className="flex flex-col items-start">
              <p className="text-sm">{n.content}</p>
              <p className="text-xs text-muted-foreground">{n.type}</p>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
