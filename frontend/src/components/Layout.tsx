import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/AppSidebar"
import { Bell, Search, Sun, Moon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useTheme } from "@/contexts/ThemeContext"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme()

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-background via-background to-accent/5">
        <AppSidebar />
        
        <div className="flex-1 flex flex-col">
          <header className="h-16 border-b border-border/40 bg-background/95 backdrop-blur-xl flex items-center justify-between px-6">
            <div className="flex items-center gap-6">
              <SidebarTrigger className="h-8 w-8 hover:bg-accent/80 rounded-lg transition-colors" />
              <div className="relative max-w-md hidden sm:block">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Search transactions, insights..." 
                  className="pl-10 bg-background/80 border-border/60 rounded-xl h-10"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={toggleTheme}
                className="rounded-xl h-10 w-10 hover:bg-accent/80"
              >
                {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
              <Button variant="ghost" size="icon" className="rounded-xl h-10 w-10 hover:bg-accent/80">
                <Bell className="h-5 w-5" />
              </Button>
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/40 rounded-xl flex items-center justify-center text-primary-foreground font-semibold text-sm">
                U
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto max-w-7xl">
            <div className="container mx-auto p-6 max-w-7xl">
              {children}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}