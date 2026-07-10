import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { Briefcase, CalendarDays, KanbanSquare, Users } from "lucide-react"
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import {
  AdminAnalyticsService,
  AdminInterviewsService,
  type ApplicationStage,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { useI18n } from "@/contexts/i18n"
import useAuth from "@/hooks/useAuth"

const STAGE_KEYS: Record<ApplicationStage, string> = {
  APPLIED: "board.applied",
  SCREENING: "board.screening",
  INTERVIEW: "board.interview",
  OFFER: "board.offer",
  HIRED: "board.hired",
  REJECTED: "board.rejected",
}

// Funnel = the positive forward flow (excludes REJECTED).
const FUNNEL_STAGES: ApplicationStage[] = [
  "APPLIED",
  "SCREENING",
  "INTERVIEW",
  "OFFER",
  "HIRED",
]

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - ATS",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const { t } = useI18n()
  const { data: calendar } = useQuery({
    queryKey: ["calendar"],
    queryFn: () => AdminInterviewsService.listCalendar(),
  })
  const { data: summary } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => AdminAnalyticsService.getSummary(),
  })

  const funnelData = FUNNEL_STAGES.map((stage) => ({
    stage: t(STAGE_KEYS[stage] as never),
    count: summary?.funnel?.[stage] ?? 0,
  }))

  const stats = [
    {
      label: t("dashboard.pendingCandidates"),
      value: summary?.pending_candidates ?? 0,
      to: "/board",
    },
    {
      label: t("dashboard.pendingFeedback"),
      value: summary?.pending_feedback ?? 0,
      to: "/interviews",
    },
    {
      label: t("analytics.openJobs"),
      value: summary?.open_jobs ?? 0,
      to: "/jobs",
    },
    {
      label: t("analytics.hired"),
      value: summary?.hired ?? 0,
      to: "/analytics",
    },
  ]

  const cards = [
    {
      to: "/jobs",
      icon: Briefcase,
      title: t("nav.jobs"),
      description: t("dashboard.welcome"),
    },
    {
      to: "/board",
      icon: KanbanSquare,
      title: t("nav.board"),
      description: t("dashboard.welcome"),
    },
    {
      to: "/candidates",
      icon: Users,
      title: t("nav.candidates"),
      description: t("dashboard.welcome"),
    },
    {
      to: "/interviews",
      icon: CalendarDays,
      title: t("nav.interviews"),
      description: t("dashboard.welcome"),
    },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          {currentUser?.name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">{t("dashboard.welcome")}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s) => (
          <RouterLink
            key={s.label}
            to={s.to}
            className="rounded-lg border p-4 transition-colors hover:bg-accent"
          >
            <p className="text-3xl font-bold">{s.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
          </RouterLink>
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("dashboard.upcomingInterviews")}
        </h2>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {(calendar ?? []).length === 0 ? (
            <p className="text-muted-foreground text-sm">
              {t("dashboard.noUpcoming")}
            </p>
          ) : (
            (calendar ?? []).map((iv) => (
              <div key={iv.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {t("dashboard.round", { n: iv.round })}
                  </span>
                  <Badge variant="secondary">{iv.status}</Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(iv.scheduled_time).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("dashboard.hiringFunnel")}
        </h2>
        <div className="rounded-lg border p-4" style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={funnelData}>
              <XAxis dataKey="stage" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("dashboard.quickLinks")}
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <RouterLink
              key={card.to}
              to={card.to}
              className="rounded-xl border p-6 transition-colors hover:bg-accent"
            >
              <card.icon className="size-8 text-muted-foreground" />
              <h2 className="mt-4 text-lg font-semibold">{card.title}</h2>
              <p className="text-sm text-muted-foreground">
                {card.description}
              </p>
            </RouterLink>
          ))}
        </div>
      </div>
    </div>
  )
}
