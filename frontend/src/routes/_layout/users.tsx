import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { AdminUsersService, type UserCreate, type UserUpdate } from "@/client"
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
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const ROLES = ["admin", "hr", "hiring_manager", "interviewer"]

export const Route = createFileRoute("/_layout/users")({
  component: UsersPage,
  head: () => ({ meta: [{ title: "Users - ATS" }] }),
})

function RoleCheckboxes({
  value,
  onChange,
}: {
  value: string[]
  onChange: (v: string[]) => void
}) {
  const toggle = (r: string) =>
    onChange(value.includes(r) ? value.filter((x) => x !== r) : [...value, r])
  return (
    <div className="flex flex-wrap gap-3">
      {ROLES.map((r) => (
        <label key={r} className="flex items-center gap-1.5 text-sm">
          <input
            type="checkbox"
            checked={value.includes(r)}
            onChange={() => toggle(r)}
          />
          {r}
        </label>
      ))}
    </div>
  )
}

function UsersPage() {
  const { user: current } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useI18n()
  const [createOpen, setCreateOpen] = useState(false)
  const [editUser, setEditUser] = useState<{
    id: string
    name: string
    roles: string[]
  } | null>(null)

  const { data } = useQuery({
    queryKey: ["users"],
    queryFn: () => AdminUsersService.listUsers({}),
  })

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [roles, setRoles] = useState<string[]>(["interviewer"])

  const createMutation = useMutation({
    mutationFn: () =>
      AdminUsersService.createUser({
        requestBody: { email, password, name, role_codes: roles } as UserCreate,
      }),
    onSuccess: () => {
      showSuccessToast(t("users.createUser"))
      queryClient.invalidateQueries({ queryKey: ["users"] })
      setCreateOpen(false)
      setEmail("")
      setPassword("")
      setName("")
      setRoles(["interviewer"])
    },
    onError: handleError.bind(showErrorToast),
  })

  const [editRoles, setEditRoles] = useState<string[]>([])
  const updateMutation = useMutation({
    mutationFn: (id: string) =>
      AdminUsersService.updateUser({
        userId: id,
        requestBody: { role_codes: editRoles } as UserUpdate,
      }),
    onSuccess: () => {
      showSuccessToast(t("common.save"))
      queryClient.invalidateQueries({ queryKey: ["users"] })
      setEditUser(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  if (!current)
    return <div className="text-muted-foreground">{t("common.loading")}</div>
  if (!current.roles?.includes("admin")) {
    return <div className="text-muted-foreground">{t("common.adminsOnly")}</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("users.title")}</h1>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>{t("users.createUser")}</Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{t("users.createTitle")}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-1.5">
                <Label>{t("candidates.name")}</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>{t("candidates.email")}</Label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label>{t("login.password")}</Label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label>{t("users.roles")}</Label>
                <RoleCheckboxes value={roles} onChange={setRoles} />
              </div>
              <LoadingButton
                loading={createMutation.isPending}
                onClick={() => createMutation.mutate()}
                className="w-full"
                disabled={!email || !password || !name}
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
              <TableHead>{t("candidates.email")}</TableHead>
              <TableHead>{t("users.roles")}</TableHead>
              <TableHead>{t("users.active")}</TableHead>
              <TableHead className="text-right">
                {t("common.actions")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.data?.map((u) => (
              <TableRow key={u.id}>
                <TableCell className="font-medium">{u.name}</TableCell>
                <TableCell>{u.email}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {u.roles?.map((r) => (
                      <Badge key={r} variant="secondary" className="text-xs">
                        {r}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell>{u.is_active ? "✓" : "-"}</TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditUser({
                        id: u.id,
                        name: u.name,
                        roles: u.roles ?? [],
                      })
                      setEditRoles(u.roles ?? [])
                    }}
                  >
                    {t("users.editRoles")}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={!!editUser} onOpenChange={(o) => !o && setEditUser(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {t("users.editRoles")} - {editUser?.name}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <RoleCheckboxes value={editRoles} onChange={setEditRoles} />
            <LoadingButton
              loading={updateMutation.isPending}
              onClick={() => editUser && updateMutation.mutate(editUser.id)}
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
