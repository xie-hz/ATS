import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminInterviewsService,
  AdminJobsService,
  AdminUsersService,
  type InterviewStatus,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/interviews")({
  component: InterviewsPage,
  head: () => ({ meta: [{ title: "Interviews - ATS" }] }),
})

function statusVariant(s: InterviewStatus) {
  return s === "COMPLETED"
    ? "default"
    : s === "CANCELLED"
      ? "destructive"
      : "secondary"
}

const selectClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"

function InterviewsPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const [createOpen, setCreateOpen] = useState(false)
  const [feedbackFor, setFeedbackFor] = useState<string | null>(null)
  const [detailFor, setDetailFor] = useState<string | null>(null)
  const [createAppOpen, setCreateAppOpen] = useState(false)
  const [appCandidateId, setAppCandidateId] = useState("")
  const [appJobId, setAppJobId] = useState("")

  const { data: ivData } = useQuery({
    queryKey: ["interviews"],
    queryFn: () => AdminInterviewsService.listInterviews({}),
  })
  const { data: appsData } = useQuery({
    queryKey: ["applications"],
    queryFn: () => AdminApplicationsService.listApplications({}),
  })
  const { data: candData } = useQuery({
    queryKey: ["candidates"],
    queryFn: () => AdminCandidatesService.listCandidates({}),
  })
  const { data: jobsData } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => AdminJobsService.listJobs({}),
  })
  const { data: usersData } = useQuery({
    queryKey: ["users"],
    queryFn: () => AdminUsersService.listUsers({}),
  })

  const candidateMap = new Map(candData?.data?.map((c) => [c.id, c.name]))
  const jobMap = new Map(jobsData?.data?.map((j) => [j.id, j.title]))
  const appMap = new Map(appsData?.data?.map((a) => [a.id, a]))
  const userMap = new Map(usersData?.data?.map((u) => [u.id, u.name]))
  const interviewers =
    usersData?.data?.filter((u) => u.roles?.includes("interviewer")) ?? []

  const [appId, setAppId] = useState("")
  const [interviewerId, setInterviewerId] = useState("")
  const [round, setRound] = useState(1)
  const [scheduled, setScheduled] = useState("")

  const createMutation = useMutation({
    mutationFn: () =>
      AdminInterviewsService.createInterview({
        requestBody: {
          application_id: appId,
          interviewer_id: interviewerId,
          round,
          scheduled_time: new Date(scheduled).toISOString(),
        },
      }),
    onSuccess: () => {
      showSuccessToast(t("interviews.schedule"))
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      setCreateOpen(false)
      setAppId("")
      setInterviewerId("")
      setRound(1)
      setScheduled("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const [score, setScore] = useState(0)
  const [recommend, setRecommend] = useState(false)
  const [comment, setComment] = useState("")
  const feedbackMutation = useMutation({
    mutationFn: (id: string) =>
      AdminInterviewsService.submitFeedback({
        interviewId: id,
        requestBody: { score, recommend, comment },
      }),
    onSuccess: () => {
      showSuccessToast(t("interviews.feedback"))
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      setFeedbackFor(null)
      setScore(0)
      setRecommend(false)
      setComment("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const createAppMutation = useMutation({
    mutationFn: () =>
      AdminApplicationsService.createApplication({
        requestBody: { candidate_id: appCandidateId, job_id: appJobId },
      }),
    onSuccess: () => {
      showSuccessToast(t("interviews.application"))
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      setCreateAppOpen(false)
      setAppCandidateId("")
      setAppJobId("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const cancelMutation = useMutation({
    mutationFn: (id: string) =>
      AdminInterviewsService.cancelInterview({ interviewId: id }),
    onSuccess: () => {
      showSuccessToast("已取消")
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const {
    data: detailFeedback,
    isLoading: detailLoading,
    isError: detailError,
    error: detailErrorObj,
  } = useQuery({
    queryKey: ["feedback", detailFor],
    queryFn: () =>
      AdminInterviewsService.getFeedback({ interviewId: detailFor! }),
    enabled: !!detailFor,
  })

  const interviews = ivData?.data ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("interviews.title")}</h1>
        <div className="flex gap-2">
          <Dialog open={createAppOpen} onOpenChange={setCreateAppOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">{t("interviews.application")}</Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{t("interviews.application")}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label>{t("candidates.name")}</Label>
                  <select
                    className={selectClass}
                    value={appCandidateId}
                    onChange={(e) => setAppCandidateId(e.target.value)}
                  >
                    <option value="">...</option>
                    {candData?.data?.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label>{t("nav.jobs")}</Label>
                  <select
                    className={selectClass}
                    value={appJobId}
                    onChange={(e) => setAppJobId(e.target.value)}
                  >
                    <option value="">...</option>
                    {jobsData?.data?.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.title}
                      </option>
                    ))}
                  </select>
                </div>
                <LoadingButton
                  loading={createAppMutation.isPending}
                  onClick={() => createAppMutation.mutate()}
                  className="w-full"
                  disabled={!appCandidateId || !appJobId}
                >
                  {t("common.create")}
                </LoadingButton>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button>{t("interviews.schedule")}</Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{t("interviews.scheduleTitle")}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label>{t("interviews.application")}</Label>
                  <select
                    className={selectClass}
                    value={appId}
                    onChange={(e) => setAppId(e.target.value)}
                  >
                    <option value="">...</option>
                    {appsData?.data?.map((a) => (
                      <option key={a.id} value={a.id}>
                        {candidateMap.get(a.candidate_id)} -{" "}
                        {jobMap.get(a.job_id)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label>{t("interviews.interviewer")}</Label>
                  <select
                    className={selectClass}
                    value={interviewerId}
                    onChange={(e) => setInterviewerId(e.target.value)}
                  >
                    <option value="">...</option>
                    {interviewers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label>{t("interviews.round")}</Label>
                  <Input
                    type="number"
                    min={1}
                    value={round}
                    onChange={(e) => setRound(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>{t("interviews.scheduledTime")}</Label>
                  <Input
                    type="datetime-local"
                    value={scheduled}
                    onChange={(e) => setScheduled(e.target.value)}
                  />
                </div>
                <LoadingButton
                  loading={createMutation.isPending}
                  onClick={() => createMutation.mutate()}
                  className="w-full"
                  disabled={!appId || !interviewerId || !scheduled}
                >
                  {t("common.create")}
                </LoadingButton>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("candidates.name")}</TableHead>
              <TableHead>{t("nav.jobs")}</TableHead>
              <TableHead>{t("interviews.interviewer")}</TableHead>
              <TableHead>{t("interviews.round")}</TableHead>
              <TableHead>{t("interviews.scheduledTime")}</TableHead>
              <TableHead>{t("common.status")}</TableHead>
              <TableHead className="text-right">
                {t("common.actions")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {interviews.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="text-center text-muted-foreground"
                >
                  {t("interviews.noInterviews")}
                </TableCell>
              </TableRow>
            ) : (
              interviews.map((iv) => {
                const app = appMap.get(iv.application_id)
                return (
                  <TableRow key={iv.id}>
                    <TableCell>
                      {candidateMap.get(app?.candidate_id || "") || "-"}
                    </TableCell>
                    <TableCell>
                      {jobMap.get(app?.job_id || "") || "-"}
                    </TableCell>
                    <TableCell>
                      {userMap.get(iv.interviewer_id || "") || "-"}
                    </TableCell>
                    <TableCell>{iv.round}</TableCell>
                    <TableCell>
                      {new Date(iv.scheduled_time).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(iv.status)}>
                        {iv.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {iv.status === "SCHEDULED" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setFeedbackFor(iv.id)
                            setScore(0)
                            setRecommend(false)
                            setComment("")
                          }}
                        >
                          {t("interviews.feedback")}
                        </Button>
                      )}
                      {iv.status === "SCHEDULED" && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 text-xs text-destructive"
                          disabled={cancelMutation.isPending}
                          onClick={() => {
                            if (
                              confirm(
                                "确认取消该面试？取消后申请将回到筛选阶段",
                              )
                            )
                              cancelMutation.mutate(iv.id)
                          }}
                        >
                          取消
                        </Button>
                      )}
                      {iv.status === "COMPLETED" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setDetailFor(iv.id)}
                        >
                          详情
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog
        open={!!feedbackFor}
        onOpenChange={(o) => !o && setFeedbackFor(null)}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t("interviews.feedbackTitle")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("interviews.score")}</Label>
              <Input
                type="number"
                min={0}
                max={100}
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="rec"
                checked={recommend}
                onChange={(e) => setRecommend(e.target.checked)}
              />
              <Label htmlFor="rec">{t("interviews.recommend")}</Label>
            </div>
            <div className="space-y-1.5">
              <Label>{t("interviews.comment")}</Label>
              <Textarea
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
            </div>
            <LoadingButton
              loading={feedbackMutation.isPending}
              onClick={() =>
                feedbackFor && feedbackMutation.mutate(feedbackFor)
              }
              className="w-full"
            >
              {t("common.save")}
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!detailFor} onOpenChange={(o) => !o && setDetailFor(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>评价详情</DialogTitle>
          </DialogHeader>
          {detailLoading ? (
            <p className="text-muted-foreground text-center py-4">加载中...</p>
          ) : detailError ? (
            <p className="text-destructive text-center py-4">
              加载失败: {String(detailErrorObj)}
            </p>
          ) : detailFeedback ? (
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">评分</span>
                <span
                  className={`text-3xl font-bold ${detailFeedback.score >= 60 ? "text-green-600" : "text-red-500"}`}
                >
                  {detailFeedback.score}
                  <span className="text-lg text-muted-foreground font-normal">
                    /100
                  </span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">是否推荐</span>
                <Badge
                  variant={detailFeedback.recommend ? "default" : "destructive"}
                >
                  {detailFeedback.recommend ? "推荐" : "不推荐"}
                </Badge>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground mb-1">评语</p>
                <p className="text-sm leading-relaxed">
                  {detailFeedback.comment || "（无评语）"}
                </p>
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  )
}
