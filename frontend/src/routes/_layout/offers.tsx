import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import {
  AdminApplicationsService,
  AdminCandidatesService,
  AdminJobsService,
  AdminOffersService,
  type OfferStatus,
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
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/offers")({
  component: OffersPage,
  head: () => ({ meta: [{ title: "Offers - ATS" }] }),
})

function statusVariant(s: OfferStatus) {
  if (s === "ACCEPTED") return "default"
  if (s === "REJECTED") return "destructive"
  return "secondary"
}

const selectClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"

function OffersPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const [open, setOpen] = useState(false)

  const { data: offersData } = useQuery({
    queryKey: ["offers"],
    queryFn: () => AdminOffersService.listOffers({}),
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

  const candidateMap = new Map(candData?.data?.map((c) => [c.id, c.name]))
  const jobMap = new Map(jobsData?.data?.map((j) => [j.id, j.title]))
  const appMap = new Map(appsData?.data?.map((a) => [a.id, a]))

  const [appId, setAppId] = useState("")
  const [salary, setSalary] = useState(0)
  const [editOfferId, setEditOfferId] = useState<string | null>(null)
  const [editSalary, setEditSalary] = useState(0)

  const createMutation = useMutation({
    mutationFn: () =>
      AdminOffersService.createOffer({
        requestBody: { application_id: appId, salary },
      }),
    onSuccess: () => {
      showSuccessToast(t("offers.create"))
      queryClient.invalidateQueries({ queryKey: ["offers"] })
      setOpen(false)
      setAppId("")
      setSalary(0)
    },
    onError: handleError.bind(showErrorToast),
  })

  const submitMutation = useMutation({
    mutationFn: (id: string) => AdminOffersService.submitOffer({ offerId: id }),
    onSuccess: () => {
      showSuccessToast(t("offers.submit"))
      queryClient.invalidateQueries({ queryKey: ["offers"] })
    },
    onError: handleError.bind(showErrorToast),
  })
  const approveMutation = useMutation({
    mutationFn: (id: string) =>
      AdminOffersService.approveOffer({ offerId: id }),
    onSuccess: () => {
      showSuccessToast(t("offers.approve"))
      queryClient.invalidateQueries({ queryKey: ["offers"] })
    },
    onError: handleError.bind(showErrorToast),
  })
  const sendMutation = useMutation({
    mutationFn: (id: string) => AdminOffersService.sendOffer({ offerId: id }),
    onSuccess: () => {
      showSuccessToast(t("offers.send"))
      queryClient.invalidateQueries({ queryKey: ["offers"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, sal }: { id: string; sal: number }) =>
      AdminOffersService.updateOffer({
        offerId: id,
        requestBody: { salary: sal },
      }),
    onSuccess: () => {
      showSuccessToast(t("common.save"))
      queryClient.invalidateQueries({ queryKey: ["offers"] })
      setEditOfferId(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  const cancelMutation = useMutation({
    mutationFn: (id: string) => AdminOffersService.cancelOffer({ offerId: id }),
    onSuccess: () => {
      showSuccessToast("已取消")
      queryClient.invalidateQueries({ queryKey: ["offers"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const offers = offersData?.data ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("offers.title")}</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>{t("offers.create")}</Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{t("offers.createTitle")}</DialogTitle>
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
                <Label>{t("offers.salary")}</Label>
                <Input
                  type="number"
                  min={0}
                  value={salary}
                  onChange={(e) => setSalary(Number(e.target.value))}
                />
              </div>
              <LoadingButton
                loading={createMutation.isPending}
                onClick={() => createMutation.mutate()}
                className="w-full"
                disabled={!appId}
              >
                {t("common.create")}
              </LoadingButton>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("candidates.name")}</TableHead>
              <TableHead>{t("nav.jobs")}</TableHead>
              <TableHead>{t("offers.salary")}</TableHead>
              <TableHead>{t("common.status")}</TableHead>
              <TableHead className="text-right">
                {t("common.actions")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {offers.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center text-muted-foreground"
                >
                  {t("offers.noOffers")}
                </TableCell>
              </TableRow>
            ) : (
              offers.map((o) => {
                const app = appMap.get(o.application_id)
                return (
                  <TableRow key={o.id}>
                    <TableCell className="font-medium">
                      {candidateMap.get(app?.candidate_id || "") || "-"}
                    </TableCell>
                    <TableCell>
                      {jobMap.get(app?.job_id || "") || "-"}
                    </TableCell>
                    <TableCell>{o.salary}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(o.status)}>
                        {o.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      {o.status === "DRAFT" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditOfferId(o.id)
                            setEditSalary(o.salary)
                          }}
                        >
                          {t("offers.salary")}
                        </Button>
                      )}
                      {o.status === "DRAFT" && (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={submitMutation.isPending}
                          onClick={() => submitMutation.mutate(o.id)}
                        >
                          {t("offers.submit")}
                        </Button>
                      )}
                      {o.status === "PENDING_APPROVAL" && (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={approveMutation.isPending}
                          onClick={() => approveMutation.mutate(o.id)}
                        >
                          {t("offers.approve")}
                        </Button>
                      )}
                      {o.status === "APPROVED" && (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={sendMutation.isPending}
                          onClick={() => sendMutation.mutate(o.id)}
                        >
                          {t("offers.send")}
                        </Button>
                      )}
                      {["DRAFT", "PENDING_APPROVAL", "APPROVED"].includes(
                        o.status,
                      ) && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive"
                          disabled={cancelMutation.isPending}
                          onClick={() => cancelMutation.mutate(o.id)}
                        >
                          取消
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
        open={!!editOfferId}
        onOpenChange={(o) => !o && setEditOfferId(null)}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t("offers.salary")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("offers.salary")}</Label>
              <Input
                type="number"
                min={0}
                value={editSalary}
                onChange={(e) => setEditSalary(Number(e.target.value))}
              />
            </div>
            <LoadingButton
              loading={updateMutation.isPending}
              onClick={() =>
                editOfferId &&
                updateMutation.mutate({ id: editOfferId, sal: editSalary })
              }
              className="w-full"
            >
              {t("common.save")}
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
