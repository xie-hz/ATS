import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { AdminAuditLogsService } from "@/client"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useI18n } from "@/contexts/i18n"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/audit-logs")({
  component: AuditLogsPage,
  head: () => ({ meta: [{ title: "Audit Logs - ATS" }] }),
})

function AuditLogsPage() {
  const { user: current } = useAuth()
  const { t } = useI18n()
  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => AdminAuditLogsService.listAuditLogs({ limit: 100 }),
  })

  if (!current)
    return <div className="text-muted-foreground">{t("common.loading")}</div>
  if (!current.roles?.includes("admin")) {
    return <div className="text-muted-foreground">{t("common.adminsOnly")}</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("audit.title")}</h1>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("audit.time")}</TableHead>
              <TableHead>{t("audit.action")}</TableHead>
              <TableHead>{t("audit.resource")}</TableHead>
              <TableHead>{t("audit.before")}</TableHead>
              <TableHead>{t("audit.after")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center text-muted-foreground"
                >
                  {t("common.loading")}
                </TableCell>
              </TableRow>
            ) : (data?.data ?? []).length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center text-muted-foreground"
                >
                  {t("audit.noLogs")}
                </TableCell>
              </TableRow>
            ) : (
              (data?.data ?? []).map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-xs">
                    {new Date(log.created_at || "").toLocaleString()}
                  </TableCell>
                  <TableCell className="font-medium">{log.action}</TableCell>
                  <TableCell>
                    {log.resource_type}
                    {log.resource_id ? `:${log.resource_id.slice(0, 8)}` : ""}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {log.before_data ? JSON.stringify(log.before_data) : "-"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {log.after_data ? JSON.stringify(log.after_data) : "-"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
