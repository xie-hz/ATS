import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { AdminCandidatesService, type CandidateCreate } from "@/client"
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
import { useI18n } from "@/contexts/i18n"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }),
  email: z.email({ message: "Invalid email" }),
  phone: z.string().optional(),
  source: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/_layout/candidates")({
  component: CandidatesPage,
  head: () => ({ meta: [{ title: "Candidates - ATS" }] }),
})

function CandidatesPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const [keyword, setKeyword] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ["candidates", keyword],
    queryFn: () =>
      AdminCandidatesService.listCandidates({
        keyword: keyword || undefined,
      }),
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", email: "", phone: "", source: "" },
  })

  const createMutation = useMutation({
    mutationFn: (data: FormData) =>
      AdminCandidatesService.createCandidate({
        requestBody: data as CandidateCreate,
      }),
    onSuccess: () => {
      showSuccessToast(t("candidates.add"))
      queryClient.invalidateQueries({ queryKey: ["candidates"] })
      setOpen(false)
      form.reset({ name: "", email: "", phone: "", source: "" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const [editCand, setEditCand] = useState<{
    id: string
    name: string
    email: string
    phone: string
    source: string
  } | null>(null)

  const editMutation = useMutation({
    mutationFn: (data: {
      id: string
      body: { name: string; email: string; phone?: string; source?: string }
    }) =>
      AdminCandidatesService.updateCandidate({
        candidateId: data.id,
        requestBody: data.body,
      }),
    onSuccess: () => {
      showSuccessToast("已更新")
      queryClient.invalidateQueries({ queryKey: ["candidates"] })
      setEditCand(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("candidates.title")}</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>{t("candidates.add")}</Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{t("candidates.addTitle")}</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit((d) => createMutation.mutate(d))}
                className="space-y-4"
              >
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("candidates.name")}</FormLabel>
                      <FormControl>
                        <Input placeholder="Jane Doe" {...field} />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("candidates.email")}</FormLabel>
                      <FormControl>
                        <Input placeholder="jane@example.com" {...field} />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("candidates.phone")}</FormLabel>
                      <FormControl>
                        <Input placeholder={t("candidates.phone")} {...field} />
                      </FormControl>
                      <FormMessage className="text-xs" />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="source"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("candidates.source")}</FormLabel>
                      <FormControl>
                        <Input placeholder="LinkedIn, Referral..." {...field} />
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

      <Input
        placeholder={t("candidates.searchPlaceholder")}
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        className="max-w-sm"
      />

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("candidates.name")}</TableHead>
              <TableHead>{t("candidates.email")}</TableHead>
              <TableHead>{t("candidates.phone")}</TableHead>
              <TableHead>{t("candidates.source")}</TableHead>
              <TableHead>{t("candidates.tags")}</TableHead>
              <TableHead className="text-right">
                {t("common.actions")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-muted-foreground"
                >
                  {t("common.loading")}
                </TableCell>
              </TableRow>
            ) : (data?.data ?? []).length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-muted-foreground"
                >
                  {t("candidates.noCandidates")}
                </TableCell>
              </TableRow>
            ) : (
              data?.data?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.name}</TableCell>
                  <TableCell>{c.email}</TableCell>
                  <TableCell>{c.phone || "-"}</TableCell>
                  <TableCell>{c.source || "-"}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {c.tags?.map((tag) => (
                        <Badge
                          key={tag}
                          variant="secondary"
                          className="text-xs"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        setEditCand({
                          id: c.id,
                          name: c.name,
                          email: c.email,
                          phone: c.phone || "",
                          source: c.source || "",
                        })
                      }
                    >
                      编辑
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={!!editCand} onOpenChange={(o) => !o && setEditCand(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>编辑候选人</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("candidates.name")}</Label>
              <Input
                value={editCand?.name || ""}
                onChange={(e) =>
                  setEditCand((p) => (p ? { ...p, name: e.target.value } : p))
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label>{t("candidates.email")}</Label>
              <Input
                type="email"
                value={editCand?.email || ""}
                onChange={(e) =>
                  setEditCand((p) => (p ? { ...p, email: e.target.value } : p))
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label>{t("candidates.phone")}</Label>
              <Input
                value={editCand?.phone || ""}
                onChange={(e) =>
                  setEditCand((p) => (p ? { ...p, phone: e.target.value } : p))
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label>{t("candidates.source")}</Label>
              <Input
                value={editCand?.source || ""}
                onChange={(e) =>
                  setEditCand((p) => (p ? { ...p, source: e.target.value } : p))
                }
              />
            </div>
            <LoadingButton
              loading={editMutation.isPending}
              className="w-full"
              onClick={() =>
                editCand &&
                editMutation.mutate({
                  id: editCand.id,
                  body: {
                    name: editCand.name,
                    email: editCand.email,
                    phone: editCand.phone || undefined,
                    source: editCand.source || undefined,
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
