import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminInterviewsService,
  AdminJobsService,
  AdminUsersService,
  type ApplicationStage,
  type InterviewStatus,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const selectClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"

const STAGE_KEYS: Record<ApplicationStage, string> = {
  APPLIED: "board.applied",
  SCREENING: "board.screening",
  INTERVIEW: "board.interview",
  OFFER: "board.offer",
  HIRED: "board.hired",
  REJECTED: "board.rejected",
}

export const Route = createFileRoute("/_layout/board")({
  component: BoardPage,
  head: () => ({ meta: [{ title: "Board - ATS" }] }),
})

function BoardPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()

  const { data: appsData } = useQuery({
    queryKey: ["applications"],
    queryFn: () => AdminApplicationsService.listApplications({}),
  })
  const { data: candidatesData } = useQuery({
    queryKey: ["candidates"],
    queryFn: () => AdminCandidatesService.listCandidates({}),
  })
  const { data: jobsData } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => AdminJobsService.listJobs({}),
  })
  const { data: ivData } = useQuery({
    queryKey: ["interviews"],
    queryFn: () => AdminInterviewsService.listInterviews({}),
  })
  const { data: usersData } = useQuery({
    queryKey: ["users"],
    queryFn: () => AdminUsersService.listUsers({}),
  })

  const candidateMap = new Map(candidatesData?.data?.map((c) => [c.id, c.name]))
  const jobMap = new Map(jobsData?.data?.map((j) => [j.id, j.title]))
  const interviewers =
    usersData?.data?.filter((u) => u.roles?.includes("interviewer")) ?? []

  // Per-application interview status. Priority: SCHEDULED (pending action) >
  // COMPLETED (awaiting decision) > CANCELLED/NO_SHOW/REJECTED. Picking purely
  // the latest-by-time interview can land on a REJECTED/CANCELLED one and hide
  // every button, so we prefer active statuses.
  const STATUS_PRIORITY: Record<string, number> = {
    SCHEDULED: 3,
    COMPLETED: 2,
    CANCELLED: 1,
    NO_SHOW: 1,
    REJECTED: 1,
  }
  const ivStatusByApp = new Map<string, InterviewStatus>()
  const ivScoreByApp = new Map<string, number>()
  const ivRecommendByApp = new Map<string, boolean>()
  const ivIdByApp = new Map<string, string>() // a COMPLETED interview id, for 详情
  ivData?.data?.forEach((iv) => {
    const aid = iv.application_id
    // First COMPLETED in the list = latest completed by scheduled_time desc.
    if (iv.status === "COMPLETED" && !ivIdByApp.has(aid)) {
      ivIdByApp.set(aid, iv.id)
    }
    const cur = ivStatusByApp.get(aid)
    if (!cur || STATUS_PRIORITY[iv.status] > STATUS_PRIORITY[cur]) {
      ivStatusByApp.set(aid, iv.status)
    }
  })
  // Fetch feedback for COMPLETED interviews to show score/recommend on cards
  const completedIvIds =
    ivData?.data
      ?.filter((i) => i.status === "COMPLETED")
      .map((i) => i.id)
      .join(",") || ""
  const { data: allFeedback } = useQuery({
    queryKey: ["board-feedback", completedIvIds],
    queryFn: async () => {
      const completed =
        ivData?.data?.filter((i) => i.status === "COMPLETED") ?? []
      const results: Record<string, { score: number; recommend: boolean }> = {}
      const seen = new Set<string>()
      for (const iv of completed) {
        if (seen.has(iv.application_id)) continue
        seen.add(iv.application_id)
        try {
          const fb = await AdminInterviewsService.getFeedback({
            interviewId: iv.id,
          })
          results[iv.application_id] = {
            score: fb.score,
            recommend: fb.recommend,
          }
        } catch {
          // skip
        }
      }
      return results
    },
    enabled: !!ivData,
  })
  if (allFeedback) {
    Object.entries(allFeedback).forEach(([appId, fb]) => {
      ivScoreByApp.set(appId, fb.score)
      ivRecommendByApp.set(appId, fb.recommend)
    })
  }
  // Find SCHEDULED interview id by application
  const findSchedIvId = (appId: string) =>
    ivData?.data?.find(
      (i) => i.application_id === appId && i.status === "SCHEDULED",
    )?.id

  // --- mutations ---
  const advanceMutation = useMutation({
    mutationFn: ({ id, target }: { id: string; target: ApplicationStage }) =>
      AdminApplicationsService.advanceApplication({
        applicationId: id,
        requestBody: { target_stage: target },
      }),
    onSuccess: () => {
      showSuccessToast(t("board.advance"))
      queryClient.invalidateQueries({ queryKey: ["applications"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const rejectMutation = useMutation({
    mutationFn: (id: string) =>
      AdminApplicationsService.rejectApplication({ applicationId: id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const restoreMutation = useMutation({
    mutationFn: (id: string) =>
      AdminApplicationsService.restoreApplication({ applicationId: id }),
    onSuccess: () => {
      showSuccessToast(t("board.restore"))
      queryClient.invalidateQueries({ queryKey: ["applications"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const scheduleMutation = useMutation({
    mutationFn: (data: {
      appId: string
      interviewerId: string
      round: number
      time: string
    }) =>
      AdminInterviewsService.createInterview({
        requestBody: {
          application_id: data.appId,
          interviewer_id: data.interviewerId,
          round: data.round,
          scheduled_time: new Date(data.time).toISOString(),
        },
      }),
    onSuccess: () => {
      showSuccessToast("面试已安排")
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      setScheduleAppId(null)
      setSchInterviewerId("")
      setSchRound(1)
      setSchTime("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const feedbackMutation = useMutation({
    mutationFn: (data: {
      ivId: string
      score: number
      recommend: boolean
      comment: string
    }) =>
      AdminInterviewsService.submitFeedback({
        interviewId: data.ivId,
        requestBody: {
          score: data.score,
          recommend: data.recommend,
          comment: data.comment,
        },
      }),
    onSuccess: () => {
      showSuccessToast("评价已提交")
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      queryClient.invalidateQueries({ queryKey: ["board-feedback"] })
      setFeedbackIvId(null)
      setFbScore(0)
      setFbRecommend(false)
      setFbComment("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const cancelIvMutation = useMutation({
    mutationFn: (ivId: string) =>
      AdminInterviewsService.cancelInterview({ interviewId: ivId }),
    onSuccess: () => {
      showSuccessToast("面试已取消")
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      queryClient.invalidateQueries({ queryKey: ["applications"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  // --- batch state ---
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [batchOpen, setBatchOpen] = useState(false)
  const [batchTarget, setBatchTarget] = useState<ApplicationStage>("SCREENING")
  const [batchInviteOpen, setBatchInviteOpen] = useState(false)
  const [biInterviewerId, setBiInterviewerId] = useState("")
  const [biRound, setBiRound] = useState(1)
  const [biStartTime, setBiStartTime] = useState("")
  const [biInterval, setBiInterval] = useState(60)
  const [batchNotifyOpen, setBatchNotifyOpen] = useState(false)
  const [notifyMessage, setNotifyMessage] = useState("")

  const batchAdvanceMutation = useMutation({
    mutationFn: ({
      ids,
      target,
    }: {
      ids: string[]
      target: ApplicationStage
    }) =>
      AdminApplicationsService.batchAdvance({
        requestBody: { application_ids: ids, target_stage: target },
      }),
    onSuccess: (res) => {
      const total = selectedIds.size
      const skipped = total - res.count
      if (res.count === 0) {
        showErrorToast(`全部跳过（${skipped} 个），请检查状态是否允许`)
      } else {
        showSuccessToast(
          skipped > 0
            ? `推进 ${res.count} 个，跳过 ${skipped} 个`
            : `推进 ${res.count} 个`,
        )
      }
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      setSelectedIds(new Set())
      setBatchOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const batchInviteMutation = useMutation({
    mutationFn: (data: {
      ids: string[]
      interviewerId: string
      round: number
      startTime: string
      interval: number
    }) =>
      AdminInterviewsService.batchCreateInterviews({
        requestBody: {
          application_ids: data.ids,
          interviewer_id: data.interviewerId,
          round: data.round,
          scheduled_time: new Date(data.startTime).toISOString(),
          interval_minutes: data.interval,
        },
      }),
    onSuccess: (res) => {
      const created = res.created ?? []
      const errs = res.errors?.length ?? 0
      if (created.length === 0) {
        showErrorToast(`全部失败（${errs} 个）`)
      } else {
        showSuccessToast(
          errs > 0
            ? `${t("board.invited", { n: created.length })}，失败 ${errs} 个`
            : t("board.invited", { n: created.length }),
        )
      }
      queryClient.invalidateQueries({ queryKey: ["applications"] })
      queryClient.invalidateQueries({ queryKey: ["interviews"] })
      setSelectedIds(new Set())
      setBatchInviteOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const batchNotifyMutation = useMutation({
    mutationFn: (data: { ids: string[]; message: string }) =>
      AdminApplicationsService.batchNotify({
        requestBody: { application_ids: data.ids, message: data.message },
      }),
    onSuccess: (res) => {
      showSuccessToast(
        t("board.notified", {
          n: res.notified ?? 0,
          skipped: res.skipped ?? 0,
        }),
      )
      setSelectedIds(new Set())
      setBatchNotifyOpen(false)
      setNotifyMessage("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  // --- schedule state ---
  const [scheduleAppId, setScheduleAppId] = useState<string | null>(null)
  const [schInterviewerId, setSchInterviewerId] = useState("")
  const [schRound, setSchRound] = useState(1)
  const [schTime, setSchTime] = useState("")

  // --- feedback state ---
  const [feedbackIvId, setFeedbackIvId] = useState<string | null>(null)
  const [fbScore, setFbScore] = useState(0)
  const [fbRecommend, setFbRecommend] = useState(false)
  const [fbComment, setFbComment] = useState("")
  const [detailIvId, setDetailIvId] = useState<string | null>(null)

  const { data: detailFeedback, isLoading: detailLoading } = useQuery({
    queryKey: ["feedback", detailIvId],
    queryFn: () =>
      AdminInterviewsService.getFeedback({ interviewId: detailIvId! }),
    enabled: !!detailIvId,
  })

  const apps = appsData?.data ?? []
  const columns: ApplicationStage[] = [
    "APPLIED",
    "SCREENING",
    "INTERVIEW",
    "OFFER",
    "HIRED",
    "REJECTED",
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("board.title")}</h1>
        <div className="flex flex-wrap gap-2">
          <Dialog open={batchOpen} onOpenChange={setBatchOpen}>
            <Button
              variant="outline"
              disabled={selectedIds.size === 0}
              onClick={() => setBatchOpen(true)}
            >
              {t("board.advance")} ({selectedIds.size})
            </Button>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{t("board.advance")}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label>{t("common.status")}</Label>
                  <select
                    className={selectClass}
                    value={batchTarget}
                    onChange={(e) =>
                      setBatchTarget(e.target.value as ApplicationStage)
                    }
                  >
                    <option value="APPLIED">APPLIED</option>
                    <option value="SCREENING">SCREENING</option>
                    <option value="INTERVIEW">INTERVIEW</option>
                    <option value="OFFER">OFFER</option>
                    <option value="HIRED">HIRED</option>
                  </select>
                </div>
                <Button
                  className="w-full"
                  disabled={batchAdvanceMutation.isPending}
                  onClick={() =>
                    batchAdvanceMutation.mutate({
                      ids: Array.from(selectedIds),
                      target: batchTarget,
                    })
                  }
                >
                  {t("board.advance")}
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={batchInviteOpen} onOpenChange={setBatchInviteOpen}>
            <Button
              variant="outline"
              disabled={selectedIds.size === 0}
              onClick={() => setBatchInviteOpen(true)}
            >
              {t("board.batchInvite")} ({selectedIds.size})
            </Button>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{t("board.batchInviteTitle")}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label>{t("interviews.interviewer")}</Label>
                  <select
                    className={selectClass}
                    value={biInterviewerId}
                    onChange={(e) => setBiInterviewerId(e.target.value)}
                  >
                    <option value="">...</option>
                    {interviewers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>{t("interviews.round")}</Label>
                    <Input
                      type="number"
                      min={1}
                      value={biRound}
                      onChange={(e) => setBiRound(Number(e.target.value))}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label>{t("board.interval")}</Label>
                    <Input
                      type="number"
                      min={1}
                      value={biInterval}
                      onChange={(e) => setBiInterval(Number(e.target.value))}
                    />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label>{t("board.startTime")}</Label>
                  <Input
                    type="datetime-local"
                    value={biStartTime}
                    onChange={(e) => setBiStartTime(e.target.value)}
                  />
                </div>
                <LoadingButton
                  loading={batchInviteMutation.isPending}
                  className="w-full"
                  disabled={!biInterviewerId || !biStartTime}
                  onClick={() =>
                    batchInviteMutation.mutate({
                      ids: Array.from(selectedIds),
                      interviewerId: biInterviewerId,
                      round: biRound,
                      startTime: biStartTime,
                      interval: biInterval,
                    })
                  }
                >
                  {t("common.create")}
                </LoadingButton>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={batchNotifyOpen} onOpenChange={setBatchNotifyOpen}>
            <Button
              variant="outline"
              disabled={selectedIds.size === 0}
              onClick={() => setBatchNotifyOpen(true)}
            >
              {t("board.batchNotify")} ({selectedIds.size})
            </Button>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{t("board.batchNotifyTitle")}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label>{t("board.notifyMessage")}</Label>
                  <Textarea
                    rows={4}
                    value={notifyMessage}
                    onChange={(e) => setNotifyMessage(e.target.value)}
                  />
                </div>
                <LoadingButton
                  loading={batchNotifyMutation.isPending}
                  className="w-full"
                  disabled={!notifyMessage.trim()}
                  onClick={() =>
                    batchNotifyMutation.mutate({
                      ids: Array.from(selectedIds),
                      message: notifyMessage,
                    })
                  }
                >
                  {t("common.create")}
                </LoadingButton>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {columns.map((stage) => {
          const items = apps
            .filter((a) => a.stage === stage)
            .sort((a, b) => {
              // 面试中阶段按推荐+分数排序
              if (stage !== "INTERVIEW") return 0
              const aRec = ivRecommendByApp.get(a.id) ? 1 : 0
              const bRec = ivRecommendByApp.get(b.id) ? 1 : 0
              if (aRec !== bRec) return bRec - aRec
              const aScore = ivScoreByApp.get(a.id) ?? 0
              const bScore = ivScoreByApp.get(b.id) ?? 0
              return bScore - aScore
            })
          return (
            <div
              key={stage}
              className="rounded-lg border bg-muted/30 p-3 min-h-[200px]"
            >
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-sm">
                  {t(STAGE_KEYS[stage] as never)}
                </h2>
                <span className="text-xs text-muted-foreground">
                  {items.length}
                </span>
              </div>
              <div className="space-y-2">
                {items.map((app) => {
                  const ivStatus = ivStatusByApp.get(app.id)
                  const schedIvId = findSchedIvId(app.id)
                  return (
                    <div
                      key={app.id}
                      className="rounded-md border bg-background p-3 space-y-2"
                    >
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={selectedIds.has(app.id)}
                          onChange={() => toggleSelect(app.id)}
                        />
                        <p className="font-medium text-sm truncate flex-1">
                          {candidateMap.get(app.candidate_id) || "-"}
                        </p>
                        {app.stage === "INTERVIEW" &&
                          ivStatus === "COMPLETED" &&
                          ivRecommendByApp.get(app.id) && (
                            <span className="text-xs text-green-600 font-medium">
                              推荐
                            </span>
                          )}
                        {app.stage === "INTERVIEW" &&
                          ivStatus === "COMPLETED" &&
                          ivScoreByApp.has(app.id) && (
                            <span className="text-sm font-bold">
                              {ivScoreByApp.get(app.id)}
                            </span>
                          )}
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {jobMap.get(app.job_id) || "-"}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {/* APPLIED -> 推进到 SCREENING */}
                        {app.stage === "APPLIED" && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs"
                            disabled={advanceMutation.isPending}
                            onClick={() =>
                              advanceMutation.mutate({
                                id: app.id,
                                target: "SCREENING",
                              })
                            }
                          >
                            {t("board.advance")}
                          </Button>
                        )}

                        {/* SCREENING -> 安排面试 + 淘汰 */}
                        {app.stage === "SCREENING" && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs"
                              onClick={() => setScheduleAppId(app.id)}
                            >
                              安排面试
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 text-xs text-destructive"
                              disabled={rejectMutation.isPending}
                              onClick={() => rejectMutation.mutate(app.id)}
                            >
                              {t("board.reject")}
                            </Button>
                          </>
                        )}

                        {/* INTERVIEW: context action + always-available 淘汰 */}
                        {app.stage === "INTERVIEW" && (
                          <>
                            {ivStatus === "SCHEDULED" && schedIvId && (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-7 text-xs"
                                  onClick={() => {
                                    setFeedbackIvId(schedIvId)
                                    setFbScore(0)
                                    setFbRecommend(false)
                                    setFbComment("")
                                  }}
                                >
                                  {t("board.evaluate")}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-7 text-xs"
                                  disabled={cancelIvMutation.isPending}
                                  onClick={() => {
                                    if (
                                      confirm(
                                        "确认取消该面试？取消后申请将回到筛选阶段",
                                      )
                                    )
                                      cancelIvMutation.mutate(schedIvId)
                                  }}
                                >
                                  {t("board.cancelInterview")}
                                </Button>
                              </>
                            )}

                            {ivStatus === "COMPLETED" && (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-7 text-xs"
                                  disabled={advanceMutation.isPending}
                                  onClick={() =>
                                    advanceMutation.mutate({
                                      id: app.id,
                                      target: "OFFER",
                                    })
                                  }
                                >
                                  {t("board.advance")}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-7 text-xs"
                                  onClick={() => {
                                    const ivId = ivIdByApp.get(app.id)
                                    if (ivId) setDetailIvId(ivId)
                                  }}
                                >
                                  {t("board.detail")}
                                </Button>
                              </>
                            )}

                            {!ivStatus && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-7 text-xs"
                                onClick={() => setScheduleAppId(app.id)}
                              >
                                {t("board.scheduleInterview")}
                              </Button>
                            )}

                            {/* 淘汰候选人：面试中任意状态都可淘汰 */}
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 text-xs text-destructive"
                              disabled={rejectMutation.isPending}
                              onClick={() => rejectMutation.mutate(app.id)}
                            >
                              {t("board.reject")}
                            </Button>
                          </>
                        )}

                        {/* OFFER -> 推进 + 淘汰 */}
                        {app.stage === "OFFER" && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs"
                              disabled={advanceMutation.isPending}
                              onClick={() =>
                                advanceMutation.mutate({
                                  id: app.id,
                                  target: "HIRED",
                                })
                              }
                            >
                              {t("board.advance")}
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 text-xs"
                              disabled={rejectMutation.isPending}
                              onClick={() => rejectMutation.mutate(app.id)}
                            >
                              {t("board.reject")}
                            </Button>
                          </>
                        )}

                        {/* REJECTED -> 恢复 */}
                        {app.stage === "REJECTED" && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs"
                            disabled={restoreMutation.isPending}
                            onClick={() => restoreMutation.mutate(app.id)}
                          >
                            {t("board.restore")}
                          </Button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>

      {/* 安排面试对话框 */}
      <Dialog
        open={!!scheduleAppId}
        onOpenChange={(o) => !o && setScheduleAppId(null)}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>安排面试</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>面试官</Label>
              <select
                className={selectClass}
                value={schInterviewerId}
                onChange={(e) => setSchInterviewerId(e.target.value)}
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
              <Label>轮次</Label>
              <Input
                type="number"
                min={1}
                value={schRound}
                onChange={(e) => setSchRound(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>面试时间</Label>
              <Input
                type="datetime-local"
                value={schTime}
                onChange={(e) => setSchTime(e.target.value)}
              />
            </div>
            <LoadingButton
              loading={scheduleMutation.isPending}
              className="w-full"
              disabled={!scheduleAppId || !schInterviewerId || !schTime}
              onClick={() =>
                scheduleAppId &&
                scheduleMutation.mutate({
                  appId: scheduleAppId,
                  interviewerId: schInterviewerId,
                  round: schRound,
                  time: schTime,
                })
              }
            >
              {t("common.create")}
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      {/* 评价对话框 */}
      <Dialog
        open={!!feedbackIvId}
        onOpenChange={(o) => !o && setFeedbackIvId(null)}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>面试评价</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>评分 (0-100)</Label>
              <Input
                type="number"
                min={0}
                max={100}
                value={fbScore}
                onChange={(e) => setFbScore(Number(e.target.value))}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="fb-rec"
                checked={fbRecommend}
                onChange={(e) => setFbRecommend(e.target.checked)}
              />
              <Label htmlFor="fb-rec">推荐</Label>
            </div>
            <div className="space-y-1.5">
              <Label>评语</Label>
              <Input
                value={fbComment}
                onChange={(e) => setFbComment(e.target.value)}
              />
            </div>
            <LoadingButton
              loading={feedbackMutation.isPending}
              className="w-full"
              onClick={() =>
                feedbackIvId &&
                feedbackMutation.mutate({
                  ivId: feedbackIvId,
                  score: fbScore,
                  recommend: fbRecommend,
                  comment: fbComment,
                })
              }
            >
              {t("common.save")}
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      {/* 评价详情对话框 */}
      <Dialog
        open={!!detailIvId}
        onOpenChange={(o) => !o && setDetailIvId(null)}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>评价详情</DialogTitle>
          </DialogHeader>
          {detailLoading ? (
            <p className="text-muted-foreground text-center py-4">加载中...</p>
          ) : detailFeedback ? (
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">评分</span>
                <span
                  className={`text-3xl font-bold ${detailFeedback.score >= 60 ? "text-green-600" : "text-red-500"}`}
                >
                  {detailFeedback.score}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">是否推荐</span>
                <span className="text-lg">
                  {detailFeedback.recommend ? "推荐" : "不推荐"}
                </span>
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
