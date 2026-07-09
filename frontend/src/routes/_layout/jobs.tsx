import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { AdminJobsService, type JobCreate, type JobStatus } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
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

const formSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  headcount: z.number().int().min(1, { message: "At least 1" }),
  location: z.string().optional(),
  description: z.string().optional(),
  requirements: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/_layout/jobs")({
  component: JobsPage,
  head: () => ({ meta: [{ title: "Jobs - ATS" }] }),
})

function statusVariant(status: JobStatus) {
  switch (status) {
    case "OPEN":
      return "default" as const
    case "CLOSED":
      return "destructive" as const
    default:
      return "secondary" as const
  }
}

function JobsPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => AdminJobsService.listJobs({}),
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      headcount: 1,
      location: "",
      description: "",
      requirements: "",
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: FormData) =>
      AdminJobsService.createJob({ requestBody: data as JobCreate }),
    onSuccess: () => {
      showSuccessToast(t("jobs.create"))
      queryClient.invalidateQueries({ queryKey: ["jobs"] })
      setOpen(false)
      form.reset({
        title: "",
        headcount: 1,
        location: "",
        description: "",
        requirements: "",
      })
    },
    onError: handleError.bind(showErrorToast),
  })

  const publishMutation = useMutation({
    mutationFn: (jobId: string) => AdminJobsService.publishJob({ jobId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: handleError.bind(showErrorToast),
  })

  const closeMutation = useMutation({
    mutationFn: (jobId: string) => AdminJobsService.closeJob({ jobId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: handleError.bind(showErrorToast),
  })

  const reopenMutation = useMutation({
    mutationFn: (jobId: string) => AdminJobsService.reopenJob({ jobId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (jobId: string) => AdminJobsService.deleteJob({ jobId }),
    onSuccess: () => {
      showSuccessToast("已删除")
      queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const [editJob, setEditJob] = useState<{
    id: string
    title: string
    headcount: number
    location: string
    description: string
    requirements: string
  } | null>(null)

  const editMutation = useMutation({
    mutationFn: (data: {
      id: string
      body: {
        title: string
        headcount: number
        location?: string
        description?: string
        requirements?: string
      }
    }) =>
      AdminJobsService.updateJob({ jobId: data.id, requestBody: data.body }),
    onSuccess: () => {
      showSuccessToast("已更新")
      queryClient.invalidateQueries({ queryKey: ["jobs"] })
      setEditJob(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => createMutation.mutate(data)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("jobs.title")}</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>{t("jobs.create")}</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>{t("jobs.createTitle")}</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4"
              >
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("jobs.jobTitle")}</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Senior Python Engineer"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="headcount"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t("jobs.headcount")}</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            min={1}
                            value={field.value}
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                          />
                        </FormControl>
                        <FormMessage className="text-xs" />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="location"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t("jobs.location")}</FormLabel>
                        <FormControl>
                          <Input placeholder="Remote" {...field} />
                        </FormControl>
                        <FormMessage className="text-xs" />
                      </FormItem>
                    )}
                  />
                </div>
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("jobs.description")}</FormLabel>
                      <FormControl>
                        <Textarea rows={3} {...field} />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="requirements"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("jobs.requirements")}</FormLabel>
                      <FormControl>
                        <Textarea rows={3} {...field} />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <LoadingButton
                  type="submit"
                  loading={createMutation.isPending}
                  className="w-full"
                >
                  {t("common.create")}
                </LoadingButton>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("jobs.jobTitle")}</TableHead>
              <TableHead>{t("jobs.headcount")}</TableHead>
              <TableHead>{t("jobs.location")}</TableHead>
              <TableHead>{t("common.status")}</TableHead>
              <TableHead className="text-right">
                {t("common.actions")}
              </TableHead>
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
                  {t("jobs.noJobs")}
                </TableCell>
              </TableRow>
            ) : (
              data?.data?.map((job) => (
                <TableRow key={job.id}>
                  <TableCell className="font-medium">{job.title}</TableCell>
                  <TableCell>{job.headcount}</TableCell>
                  <TableCell>{job.location || "-"}</TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(job.status)}>
                      {job.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    {(job.status === "DRAFT" ||
                      job.status === "PENDING_APPROVAL") && (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={publishMutation.isPending}
                        onClick={() => publishMutation.mutate(job.id)}
                      >
                        {t("jobs.publish")}
                      </Button>
                    )}
                    {job.status === "CLOSED" ? (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={reopenMutation.isPending}
                        onClick={() => reopenMutation.mutate(job.id)}
                      >
                        重新打开
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={closeMutation.isPending}
                        onClick={() => closeMutation.mutate(job.id)}
                      >
                        {t("jobs.close")}
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        setEditJob({
                          id: job.id,
                          title: job.title,
                          headcount: job.headcount ?? 1,
                          location: job.location || "",
                          description: job.description || "",
                          requirements: job.requirements || "",
                        })
                      }
                    >
                      编辑
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-destructive"
                      disabled={deleteMutation.isPending}
                      onClick={() => {
                        if (confirm("确认删除该职位？"))
                          deleteMutation.mutate(job.id)
                      }}
                    >
                      删除
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={!!editJob} onOpenChange={(o) => !o && setEditJob(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>编辑职位</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("jobs.jobTitle")}</Label>
              <Input
                value={editJob?.title || ""}
                onChange={(e) =>
                  setEditJob((p) => (p ? { ...p, title: e.target.value } : p))
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>{t("jobs.headcount")}</Label>
                <Input
                  type="number"
                  min={1}
                  value={editJob?.headcount ?? 1}
                  onChange={(e) =>
                    setEditJob((p) =>
                      p ? { ...p, headcount: Number(e.target.value) } : p,
                    )
                  }
                />
              </div>
              <div className="space-y-1.5">
                <Label>{t("jobs.location")}</Label>
                <Input
                  value={editJob?.location || ""}
                  onChange={(e) =>
                    setEditJob((p) =>
                      p ? { ...p, location: e.target.value } : p,
                    )
                  }
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>{t("jobs.description")}</Label>
              <Textarea
                rows={3}
                value={editJob?.description || ""}
                onChange={(e) =>
                  setEditJob((p) =>
                    p ? { ...p, description: e.target.value } : p,
                  )
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label>{t("jobs.requirements")}</Label>
              <Textarea
                rows={3}
                value={editJob?.requirements || ""}
                onChange={(e) =>
                  setEditJob((p) =>
                    p ? { ...p, requirements: e.target.value } : p,
                  )
                }
              />
            </div>
            <LoadingButton
              loading={editMutation.isPending}
              className="w-full"
              onClick={() =>
                editJob &&
                editMutation.mutate({
                  id: editJob.id,
                  body: {
                    title: editJob.title,
                    headcount: editJob.headcount,
                    location: editJob.location || undefined,
                    description: editJob.description || undefined,
                    requirements: editJob.requirements || undefined,
                  },
                })
              }
            >
              {t("common.save")}
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
