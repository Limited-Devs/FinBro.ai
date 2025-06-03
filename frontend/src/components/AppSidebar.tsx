import { Home, BarChart3, MessageCircle, User, TrendingUp, CreditCard, Target, FileBarChart } from "lucide-react"
import { NavLink, useLocation } from "react-router-dom"
import { cn } from "@/services/utils"
import { useTheme } from "@/contexts/ThemeContext"

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

const otherItems = [
  { title: "AI Financial Report", url: "/financial-report", icon: FileBarChart },
  { title: "AI Assistant", url: "/chat", icon: MessageCircle },
  { title: "Profile", url: "/profile", icon: User },
]

export function AppSidebar() {
  const { state } = useSidebar()
  const location = useLocation()
  const currentPath = location.pathname
  const isCollapsed = state === "collapsed"
  const { theme } = useTheme()
  // Fixed function to properly handle NavLink's isActive
  const getNavCls = (isActive, isDisabled = false) =>
    cn(
      "transition-colors flex items-center",
      isActive
        ? "bg-primary text-primary-foreground hover:bg-primary/90 font-medium"
        : isDisabled
          ? theme === 'light'
            ? "text-slate-400 cursor-not-allowed"
            : "text-sidebar-foreground/40 cursor-not-allowed"
          : theme === 'light'
            ? "text-black-900 hover:bg-slate-100 hover:text-slate-950"
            : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
    )
  // Helper to render menu items with disabled state
  const renderMenuItem = (item, isActive, isDisabled = false) => {
    const IconComponent = item.icon;
    return (
      <SidebarMenuItem key={item.title}>
        <SidebarMenuButton asChild className="h-10 rounded-lg" disabled={isDisabled}>
          <NavLink to={item.url} end className={() => getNavCls(isActive, isDisabled)} tabIndex={isDisabled ? -1 : 0}>
            <IconComponent className={cn(
              "h-5 w-5 flex-shrink-0 min-w-[20px]", 
              isDisabled 
                ? (theme === 'light' ? 'text-slate-400' : 'text-sidebar-foreground/40') 
                : isActive
                  ? (theme === 'light' ? 'text-slate-900' : 'text-primary-foreground') // Changed for active icon in light mode
                  : theme === 'light' 
                    ? 'text-slate-900' 
                    : 'text-sidebar-foreground'
            )} />
            {!isCollapsed && <span className="font-medium ml-3">{item.title}</span>}
          </NavLink>
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }

  return (
    <Sidebar
      className={cn(
        isCollapsed ? "w-14" : "w-64",
        theme === 'light' ? "bg-white border-r border-slate-200" : "bg-sidebar border-r border-sidebar-border"
      )}
      collapsible="icon"
    >
      <SidebarContent className={theme === 'light' ? 'bg-white' : 'bg-sidebar'}>
        <div className="p-4 border-b" style={{ borderColor: theme === 'light' ? '#e5e7eb' : undefined }}>
          <h2 className={`font-bold text-xl ${theme === 'light' ? 'text-slate-800' : 'text-sidebar-foreground'} ${isCollapsed ? 'hidden' : 'block'}`}>
            FinBro.ai
          </h2>
          {isCollapsed && (
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-primary-foreground" />
            </div>
          )}
        </div>

        <div className="flex-1 overflow-auto py-4">
          <SidebarGroup>
            <SidebarGroupLabel className={`${isCollapsed ? 'hidden' : 'block'} ${theme === 'light' ? 'text-slate-500' : 'text-sidebar-foreground/70'} px-4 mb-2`}>
              Overview
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="px-2 space-y-1">
                {mainItems.map((item) => {
                  const isActive = currentPath === item.url || (item.url === "/" && currentPath === "/");
                  return renderMenuItem(item, isActive, false);
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          <SidebarGroup className="mt-6">
            <SidebarGroupLabel className={`${isCollapsed ? 'hidden' : 'block'} ${theme === 'light' ? 'text-slate-500' : 'text-sidebar-foreground/70'} px-4 mb-2`}>
              AI Tools
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="px-2 space-y-1">
                {otherItems.map((item) => {
                  const isActive = currentPath === item.url;
                  return renderMenuItem(item, isActive, false);
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </div>
      </SidebarContent>
    </Sidebar>
  )
}