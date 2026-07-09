import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { BarChart3 } from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { AdminAnalyticsService } from "@/client"
import { useI18n } from "@/contexts/i18n"

export const Route = createFileRoute("/_layout/analytics")({
  component: AnalyticsPage,
  head: () => ({ meta: [{ title: "Analytics - ATS" }] }),
})

function AnalyticsPage() {
  const { t } = useI18n()
  const { data, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => AdminAnalyticsService.getSummary(),
  })

  const funnelData = Object.entries(data?.funnel ?? {}).map(
    ([stage, count]) => ({
      stage,
      count: count as number,
    }),
  )
  const channelData = Object.entries(data?.channels ?? {}).map(
    ([source, count]) => ({ source, count: count as number }),
  )

  const stats = data
    ? [
        { label: t("analytics.jobs"), value: data.total_jobs },
        { label: t("analytics.openJobs"), value: data.open_jobs },
        { label: t("analytics.candidates"), value: data.total_candidates },
        { label: t("analytics.applications"), value: data.total_applications },
        { label: t("analytics.hired"), value: data.hired },
        { label: t("analytics.conversion"), value: data.conversion_rate },
      ]
    : []

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-2">
        <BarChart3 className="size-6" />
        <h1 className="text-2xl font-bold">{t("analytics.title")}</h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {isLoading
          ? t("common.loading")
          : stats.map((s) => (
              <div key={s.label} className="rounded-lg border p-4">
                <p className="text-2xl font-bold">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">
          {t("analytics.hiringFunnel")}
        </h2>
        <div className="rounded-lg border p-4" style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={funnelData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
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
          {t("analytics.byChannel")}
        </h2>
        <div className="rounded-lg border p-4" style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={channelData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="source" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
