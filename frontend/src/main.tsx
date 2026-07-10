import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { AdminAuthService, ApiError, OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import { I18nProvider } from "./contexts/i18n"
import { PortalAuthProvider } from "./contexts/portal-auth"
import "./index.css"
import { routeTree } from "./routeTree.gen"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  // Portal (candidate) pages use a separate portal token.
  if (window.location.pathname.startsWith("/portal")) {
    return localStorage.getItem("portal_token") || ""
  }
  return localStorage.getItem("access_token") || ""
}

const handleApiError = async (error: Error) => {
  if (!(error instanceof ApiError) || error.status !== 401) return
  const isPortal = window.location.pathname.startsWith("/portal")
  if (isPortal) {
    localStorage.removeItem("portal_token")
    window.location.href = "/portal/login"
    return
  }
  const refresh = localStorage.getItem("refresh_token")
  if (refresh) {
    try {
      const res = await AdminAuthService.refreshToken({
        requestBody: { refresh_token: refresh },
      })
      localStorage.setItem("access_token", res.access_token)
      localStorage.setItem("refresh_token", res.refresh_token)
      window.location.reload()
      return
    } catch {
      // refresh failed -> fall through to logout
    }
  }
  localStorage.removeItem("access_token")
  localStorage.removeItem("refresh_token")
  window.location.href = "/login"
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <I18nProvider>
      <PortalAuthProvider>
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
          <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
            <Toaster richColors closeButton />
          </QueryClientProvider>
        </ThemeProvider>
      </PortalAuthProvider>
    </I18nProvider>
  </StrictMode>,
)
