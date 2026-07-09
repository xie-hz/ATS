import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import {
  AdminAuthService,
  AdminUsersService,
  type Body_admin_auth_login as LoginCredentials,
  type UserPublic,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: AdminUsersService.readUserMe,
    enabled: isLoggedIn(),
  })

  const login = async (data: LoginCredentials) => {
    const response = await AdminAuthService.login({ formData: data })
    localStorage.setItem("access_token", response.access_token)
    localStorage.setItem("refresh_token", response.refresh_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    queryClient.clear()
    navigate({ to: "/login" })
  }

  return {
    loginMutation,
    logout,
    user,
  }
}

export { isLoggedIn }
export default useAuth
