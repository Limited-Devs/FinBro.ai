import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/AppSidebar"
import { Bell, Search, Sun, Moon, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useTheme } from "@/contexts/ThemeContext"
import { useAuth } from "@/contexts/AuthContext"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme()
  const { isDemo } = useAuth()

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full gradient-mesh-animated">
        {/* Subtle grid pattern overlay */}
        <div className="fixed inset-0 grid-pattern pointer-events-none" />

        <AppSidebar />

        <div className="flex-1 flex flex-col relative">
          {/* Premium Glassmorphism Header */}
          <header className="h-16 border-b border-border/30 glass sticky top-0 z-40 flex items-center justify-between px-6">
            <div className="flex items-center gap-6">
              <SidebarTrigger className="h-9 w-9 hover:bg-muted/80 rounded-xl transition-all duration-200 hover:scale-105" />

              {/* Enhanced Search Input */}
              <div className="relative max-w-md hidden sm:block group">
                <Search className="absolute left-3.5 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                <Input
                  placeholder="Search transactions, insights..."
                  className="pl-10 pr-4 bg-muted/50 border-border/50 rounded-xl h-10 w-72 
                    focus:bg-muted/80 focus:border-primary/50 focus:ring-2 focus:ring-primary/20
                    transition-all duration-300 placeholder:text-muted-foreground/60
                    hover:bg-muted/60 hover:border-border"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Demo Mode Indicator */}
              {isDemo && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-yellow-100 border border-yellow-200 mr-2">
                  <span className="text-xs font-bold text-yellow-800">DEMO MODE</span>
                </div>
              )}

              {/* AI Status Indicator */}
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary/10 border border-secondary/20 mr-2">
                <Sparkles className="h-3.5 w-3.5 text-secondary animate-pulse" />
                <span className="text-xs font-medium text-secondary">AI Active</span>
              </div>

              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                className="rounded-xl h-10 w-10 hover:bg-muted/80 transition-all duration-200 hover:scale-105"
              >
                {theme === 'dark' ? (
                  <Sun className="h-5 w-5 text-primary transition-transform hover:rotate-45" />
                ) : (
                  <Moon className="h-5 w-5 transition-transform hover:-rotate-12" />
                )}
              </Button>

              {/* Notifications */}
              <Button
                variant="ghost"
                size="icon"
                className="rounded-xl h-10 w-10 hover:bg-muted/80 relative transition-all duration-200 hover:scale-105"
              >
                <Bell className="h-5 w-5" />
                {/* Notification dot */}
                <span className="absolute top-2 right-2 h-2 w-2 bg-primary rounded-full animate-pulse" />
              </Button>

              {/* User Avatar with Status Ring */}
              <div className="relative ml-1">
                <div className="w-10 h-10 bg-gradient-to-br from-primary via-primary/80 to-secondary/60 rounded-xl 
                  flex items-center justify-center text-primary-foreground font-display font-bold text-sm
                  ring-2 ring-primary/20 ring-offset-2 ring-offset-background
                  transition-all duration-300 hover:ring-primary/40 hover:scale-105 cursor-pointer">
                  U
                </div>
                {/* Online Status */}
                <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-success rounded-full border-2 border-background" />
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 overflow-auto">
            <div className="container mx-auto p-6 max-w-7xl">
              {children}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}