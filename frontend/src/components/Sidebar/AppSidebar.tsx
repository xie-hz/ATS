import {
  BarChart3,
  Briefcase,
  CalendarDays,
  FileText,
  History,
  Home,
  KanbanSquare,
  Settings,
  Users,
} from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import { useI18n } from "@/contexts/i18n"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

export function AppSidebar() {
  const { user: currentUser } = useAuth()
  const { t } = useI18n()
  const roles = currentUser?.roles ?? []
  const isAdmin = roles.includes("admin")
  // Interviewer-only users see a minimal sidebar (just their interviews).
  const isInterviewerOnly =
    roles.includes("interviewer") &&
    !roles.includes("admin") &&
    !roles.includes("hr") &&
    !roles.includes("hiring_manager")

  const baseItems: Item[] = isInterviewerOnly
    ? [
        { icon: Home, title: t("nav.dashboard"), path: "/" },
        { icon: CalendarDays, title: t("nav.interviews"), path: "/interviews" },
        { icon: Settings, title: t("nav.settings"), path: "/settings" },
      ]
    : [
        { icon: Home, title: t("nav.dashboard"), path: "/" },
        { icon: Briefcase, title: t("nav.jobs"), path: "/jobs" },
        { icon: KanbanSquare, title: t("nav.board"), path: "/board" },
        { icon: Users, title: t("nav.candidates"), path: "/candidates" },
        { icon: CalendarDays, title: t("nav.interviews"), path: "/interviews" },
        { icon: FileText, title: t("nav.offers"), path: "/offers" },
        { icon: BarChart3, title: t("nav.analytics"), path: "/analytics" },
        { icon: Settings, title: t("nav.settings"), path: "/settings" },
      ]

  const items = isAdmin
    ? [
        ...baseItems,
        { icon: History, title: t("nav.auditLogs"), path: "/audit-logs" },
        { icon: Users, title: t("nav.users"), path: "/users" },
      ]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
