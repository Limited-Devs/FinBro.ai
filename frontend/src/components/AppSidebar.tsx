import { Home, BarChart3, MessageCircle, User, TrendingUp, CreditCard, Target, FileBarChart, Sparkles } from "lucide-react"
import { NavLink, useLocation } from "react-router-dom"
import { cn } from "@/services/utils"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

const mainItems = [
  { title: "Dashboard", url: "/", icon: Home },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "Expenses", url: "/expenses", icon: CreditCard },
  { title: "Savings Goals", url: "/savings", icon: Target },
]

const aiItems = [
  { title: "AI Financial Report", url: "/financial-report", icon: FileBarChart },
  { title: "AI Assistant", url: "/chat", icon: MessageCircle },
]

const otherItems = [
  { title: "Profile", url: "/profile", icon: User },
]

export function AppSidebar() {
  const { state } = useSidebar()
  const location = useLocation()
  const currentPath = location.pathname
  const isCollapsed = state === "collapsed"

  const getNavCls = (isActive: boolean) =>
    cn(
      "transition-all duration-200 flex items-center group relative",
      isActive
        ? "bg-primary/10 text-primary font-semibold"
        : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
    )

  const renderMenuItem = (item: typeof mainItems[0], isActive: boolean) => {
    const IconComponent = item.icon;
    return (
      <SidebarMenuItem key={item.title}>
        <SidebarMenuButton asChild className="h-11 rounded-xl overflow-hidden">
          <NavLink to={item.url} end className={() => getNavCls(isActive)}>
            {/* Active indicator bar */}
            {isActive && (
              <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-r-full" />
            )}
            <IconComponent className={cn(
              "h-5 w-5 flex-shrink-0 min-w-[20px] transition-all duration-200",
              isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
              isCollapsed && "ml-0.5"
            )} />
            {!isCollapsed && (
              <span className={cn(
                "ml-3 transition-all duration-200",
                isActive && "text-primary"
              )}>
                {item.title}
              </span>
            )}
          </NavLink>
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }

  return (
    <Sidebar
      className={cn(
        isCollapsed ? "w-16" : "w-64",
        "bg-sidebar border-r border-sidebar-border transition-all duration-300"
      )}
      collapsible="icon"
    >
      <SidebarContent className="bg-sidebar">
        {/* Logo Section */}
        <div className={cn(
          "p-4 border-b border-sidebar-border",
          isCollapsed ? "px-2" : "px-4"
        )}>
          {!isCollapsed ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary via-primary/80 to-secondary/60 rounded-xl 
                flex items-center justify-center shadow-glow-sm">
                <TrendingUp className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h2 className="font-display font-bold text-lg text-sidebar-foreground tracking-tight">
                  FinBro<span className="text-primary">.ai</span>
                </h2>
                <p className="text-[10px] text-muted-foreground -mt-0.5 uppercase tracking-widest">
                  Wealth Intelligence
                </p>
              </div>
            </div>
          ) : (
            <div className="w-10 h-10 mx-auto bg-gradient-to-br from-primary via-primary/80 to-secondary/60 rounded-xl 
              flex items-center justify-center shadow-glow-sm">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-auto py-4">
          {/* Main Navigation */}
          <SidebarGroup>
            <SidebarGroupLabel className={cn(
              "px-4 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70",
              isCollapsed && "sr-only"
            )}>
              Overview
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="px-2 space-y-1">
                {mainItems.map((item) => {
                  const isActive = currentPath === item.url || (item.url === "/" && currentPath === "/");
                  return renderMenuItem(item, isActive);
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {/* AI Tools Section */}
          <SidebarGroup className="mt-6">
            <SidebarGroupLabel className={cn(
              "px-4 mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider",
              isCollapsed && "sr-only"
            )}>
              <Sparkles className="h-3 w-3 text-secondary" />
              <span className="text-secondary">AI Tools</span>
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="px-2 space-y-1">
                {aiItems.map((item) => {
                  const isActive = currentPath === item.url;
                  return renderMenuItem(item, isActive);
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {/* Other */}
          <SidebarGroup className="mt-6">
            <SidebarGroupLabel className={cn(
              "px-4 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70",
              isCollapsed && "sr-only"
            )}>
              Account
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="px-2 space-y-1">
                {otherItems.map((item) => {
                  const isActive = currentPath === item.url;
                  return renderMenuItem(item, isActive);
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </div>

        {/* Bottom Section - Pro Badge */}
        {!isCollapsed && (
          <div className="p-4 border-t border-sidebar-border">
            <div className="gradient-border p-3 rounded-xl bg-gradient-to-br from-muted/50 to-muted/30">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="text-xs font-semibold text-foreground">Pro Features</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Unlock advanced AI predictions and unlimited reports.
              </p>
            </div>
          </div>
        )}
      </SidebarContent>
    </Sidebar>
  )
}