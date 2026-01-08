import React, { useMemo, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, DollarSign, AlertTriangle, Zap, Sparkles, ArrowUpRight, ArrowDownRight, Brain, BarChart3 } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsBarTooltip, ResponsiveContainer as BarResponsiveContainer } from 'recharts'
import { useUserData } from '@/hooks/useUserData'
import { useTrendsData } from '@/hooks/useTrendsData'
import { cn, safeNumber, formatNumber } from '@/services/utils'

// Animated counter hook for financial figures
function useAnimatedCounter(end: number, duration: number = 1500) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (end === 0) return;

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * end));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return count;
}

// Premium chart colors matching Obsidian Luxe
const CHART_COLORS = {
  gold: '#F59E0B',
  cyan: '#06B6D4',
  purple: '#A855F7',
  emerald: '#10B981',
  rose: '#F43F5E',
  orange: '#F97316',
  blue: '#3B82F6',
  pink: '#EC4899',
  teal: '#14B8A6',
};

const Dashboard = () => {
  const { data: userDataResponse, isLoading, error: queryError } = useUserData()
  const { data: trendsData, isLoading: trendsLoading } = useTrendsData(6)

  const latestPrediction = useMemo(() =>
    userDataResponse?.predictions?.[userDataResponse.predictions.length - 1],
    [userDataResponse]
  )

  const displayUserData = useMemo(() => latestPrediction?.input, [latestPrediction])
  const mlDisplayResults = useMemo(() => latestPrediction?.output, [latestPrediction])

  // Animated values
  const animatedIncome = useAnimatedCounter(displayUserData?.Income || 0);
  const animatedSavings = useAnimatedCounter(displayUserData?.Actual_Savings_Potential || 0);
  const animatedGoal = useAnimatedCounter(mlDisplayResults?.amount_model?.recommended_savings || 0);

  const expenseData = useMemo(() => {
    if (!displayUserData) return []
    return [
      { name: 'Rent', value: displayUserData.Rent || 0, color: CHART_COLORS.gold },
      { name: 'Groceries', value: displayUserData.Groceries || 0, color: CHART_COLORS.emerald },
      { name: 'Utilities', value: displayUserData.Utilities || 0, color: CHART_COLORS.cyan },
      { name: 'Transport', value: displayUserData.Transport || 0, color: CHART_COLORS.orange },
      { name: 'Insurance', value: displayUserData.Insurance || 0, color: CHART_COLORS.blue },
      { name: 'Eating Out', value: displayUserData.Eating_Out || 0, color: CHART_COLORS.rose },
      { name: 'Healthcare', value: displayUserData.Healthcare || 0, color: CHART_COLORS.teal },
      { name: 'Entertainment', value: displayUserData.Entertainment || 0, color: CHART_COLORS.purple },
      { name: 'Miscellaneous', value: displayUserData.Miscellaneous || 0, color: CHART_COLORS.pink },
    ].filter(expense => expense.value > 0)
  }, [displayUserData])

  // Real savings data from API trends endpoint
  const savingsData = useMemo(() => {
    if (!trendsData?.monthly_data || trendsData.monthly_data.length === 0) return []
    return trendsData.monthly_data.map(m => ({
      month: m.month,
      actual: m.actual_savings,
      target: m.target_savings
    }))
  }, [trendsData])

  const highestNonEssentialExpense = useMemo(() => {
    if (!displayUserData) return null

    const nonEssentialExpenses = [
      { name: 'Entertainment', value: displayUserData.Entertainment || 0 },
      { name: 'Eating Out', value: displayUserData.Eating_Out || 0 },
      { name: 'Miscellaneous', value: displayUserData.Miscellaneous || 0 }
    ]

    const highest = nonEssentialExpenses.reduce((max, expense) =>
      expense.value > max.value ? expense : max
    )

    return highest.value > 0 ? highest.name : 'non-essential'
  }, [displayUserData])

  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Loading skeleton with shimmer effect */}
        <div className="h-20 rounded-2xl shimmer" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 rounded-2xl shimmer" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-96 rounded-2xl shimmer" style={{ animationDelay: `${(i + 4) * 0.1}s` }} />
          ))}
        </div>
      </div>
    )
  }

  if (queryError) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Card className="max-w-md w-full border-destructive/30 bg-destructive/5">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertTriangle className="h-8 w-8 text-destructive" />
            </div>
            <h3 className="font-display text-lg font-semibold mb-2">Unable to Load Data</h3>
            <p className="text-sm text-muted-foreground">{(queryError as Error).message}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!displayUserData || !mlDisplayResults) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Card className="max-w-md w-full gradient-border">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <DollarSign className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="font-display text-lg font-semibold mb-2">No Financial Data</h3>
            <p className="text-sm text-muted-foreground">Complete your financial profile to see insights.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const savingsGoalProgress = displayUserData.Actual_Savings_Potential && mlDisplayResults.amount_model.recommended_savings
    ? (displayUserData.Actual_Savings_Potential / mlDisplayResults.amount_model.recommended_savings) * 100
    : 0

  return (
    <div className="space-y-8">
      {/* Premium Header */}
      <div className="animate-fade-in">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight">
              Financial Dashboard
            </h1>
            <p className="text-muted-foreground mt-1">
              Welcome back! Here's your wealth overview for this month.
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-success/10 text-success">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="font-medium">AI Analysis Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Metrics - Staggered Animation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Income - Hero Card */}
        <Card className={cn(
          "animate-fade-in stagger-1 card-hover wealth-pulse",
          "border-primary/20 bg-gradient-to-br from-card to-card/80"
        )}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Income</CardTitle>
            <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center">
              <DollarSign className="h-5 w-5 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-3xl font-bold tracking-tight">
                ${formatNumber(animatedIncome)}
              </span>
              <span className="flex items-center text-xs text-success font-medium">
                <ArrowUpRight className="h-3 w-3" />
                5.2%
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Monthly income</p>
          </CardContent>
        </Card>

        {/* Potential Savings */}
        <Card className={cn(
          "animate-fade-in stagger-2 card-hover",
          "border-secondary/20"
        )}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Potential Savings</CardTitle>
            <div className="h-9 w-9 rounded-xl bg-secondary/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-secondary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-3xl font-bold tracking-tight">
                ${formatNumber(animatedSavings)}
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Based on spending analysis</p>
          </CardContent>
        </Card>

        {/* Savings Goal */}
        <Card className={cn(
          "animate-fade-in stagger-3 card-hover",
          "border-accent/20"
        )}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">AI Savings Goal</CardTitle>
            <div className="h-9 w-9 rounded-xl bg-accent/10 flex items-center justify-center">
              <Zap className="h-5 w-5 text-accent" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-3xl font-bold tracking-tight">
                ${formatNumber(animatedGoal)}
              </span>
            </div>
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium text-foreground">{formatNumber(savingsGoalProgress, 0)}%</span>
              </div>
              <Progress value={savingsGoalProgress} className="h-2" />
            </div>
          </CardContent>
        </Card>

        {/* Financial Stress */}
        <Card className={cn(
          "animate-fade-in stagger-4 card-hover",
          displayUserData.Financial_Stress_Score > 0.5 ? "border-destructive/30" : "border-success/30"
        )}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Financial Stress</CardTitle>
            <div className={cn(
              "h-9 w-9 rounded-xl flex items-center justify-center",
              displayUserData.Financial_Stress_Score > 0.5 ? "bg-destructive/10" : "bg-success/10"
            )}>
              <AlertTriangle className={cn(
                "h-5 w-5",
                displayUserData.Financial_Stress_Score > 0.5 ? "text-destructive" : "text-success"
              )} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-3xl font-bold tracking-tight">
                {formatNumber(safeNumber(displayUserData.Financial_Stress_Score) * 100, 0)}%
              </span>
              {displayUserData.Financial_Stress_Score <= 0.3 && (
                <span className="flex items-center text-xs text-success font-medium">
                  <ArrowDownRight className="h-3 w-3" />
                  Low
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Lower is better</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Expense Breakdown */}
        <Card className="animate-fade-in stagger-5 card-hover">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-display text-lg">Expense Breakdown</CardTitle>
                <p className="text-sm text-muted-foreground mt-0.5">Monthly spending by category</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenseData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  innerRadius={60}
                  paddingAngle={2}
                  label={({ name, percent }) => `${name} ${formatNumber(safeNumber(percent) * 100, 0)}%`}
                  labelLine={{ stroke: 'hsl(var(--muted-foreground))', strokeWidth: 1 }}
                >
                  {expenseData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.color}
                      stroke="hsl(var(--background))"
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <RechartsTooltip
                  formatter={(value: number) => [`$${formatNumber(value)}`, 'Amount']}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  iconSize={8}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Savings Progress */}
        <Card className="animate-fade-in stagger-6 card-hover">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-display text-lg">Savings Progress</CardTitle>
                <p className="text-sm text-muted-foreground mt-0.5">
                  {savingsData.length > 0 ? `Last ${savingsData.length} months performance` : 'Historical performance'}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="h-[350px]">
            {savingsData.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <BarChart3 className="h-12 w-12 text-muted-foreground/50 mb-3" />
                <p className="text-sm text-muted-foreground">Insufficient historical data</p>
                <p className="text-xs text-muted-foreground/70 mt-1">Add more financial predictions to see trends</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={savingsData} barCategoryGap="20%">
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="hsl(var(--border))"
                  />
                  <XAxis
                    dataKey="month"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                    tickFormatter={(value) => `$${value / 1000}k`}
                  />
                  <RechartsBarTooltip
                    formatter={(value: number) => [`$${formatNumber(value)}`, '']}
                    cursor={{ fill: 'hsl(var(--muted))', opacity: 0.3 }}
                  />
                  <Legend
                    verticalAlign="top"
                    height={36}
                    iconType="circle"
                    iconSize={8}
                  />
                  <Bar
                    dataKey="actual"
                    fill={CHART_COLORS.gold}
                    name="Actual Savings"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="target"
                    fill={CHART_COLORS.cyan}
                    name="Target Savings"
                    radius={[4, 4, 0, 0]}
                    opacity={0.6}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Insights Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Savings Insight */}
        <Card className={cn(
          "animate-fade-in stagger-7 card-hover gradient-border",
          mlDisplayResults.savings_model?.can_achieve_savings ? "bg-success/5" : "bg-warning/5"
        )}>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-secondary/10 flex items-center justify-center">
                <Brain className="h-4 w-4 text-secondary" />
              </div>
              <CardTitle className="font-display text-base">AI Savings Insight</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {mlDisplayResults.savings_model?.can_achieve_savings ? (
              <p className="text-success text-sm leading-relaxed">
                <span className="font-semibold">Great news!</span> Our AI indicates you're on track to achieve your savings goals.
              </p>
            ) : (
              <p className="text-warning text-sm leading-relaxed">
                <span className="font-semibold">Heads up:</span> Achieving your current savings goals might be challenging. Consider reviewing expenses.
              </p>
            )}
            <div className="mt-4 flex items-center gap-2">
              <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-secondary rounded-full transition-all duration-1000"
                  style={{ width: `${mlDisplayResults.savings_model?.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs font-mono text-muted-foreground">
                {formatNumber(safeNumber(mlDisplayResults.savings_model?.confidence) * 100, 0)}% confidence
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Risk Assessment */}
        <Card className={cn(
          "animate-fade-in stagger-8 card-hover gradient-border",
          mlDisplayResults.multi_task_model?.financial_risk ? "bg-destructive/5" : "bg-success/5"
        )}>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className={cn(
                "h-8 w-8 rounded-lg flex items-center justify-center",
                mlDisplayResults.multi_task_model?.financial_risk ? "bg-destructive/10" : "bg-success/10"
              )}>
                <AlertTriangle className={cn(
                  "h-4 w-4",
                  mlDisplayResults.multi_task_model?.financial_risk ? "text-destructive" : "text-success"
                )} />
              </div>
              <CardTitle className="font-display text-base">AI Risk Assessment</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {mlDisplayResults.multi_task_model?.financial_risk ? (
              <p className="text-destructive text-sm leading-relaxed">
                <span className="font-semibold">Alert:</span> Potential financial risk detected. Review your financial situation.
              </p>
            ) : (
              <p className="text-success text-sm leading-relaxed">
                <span className="font-semibold">All clear!</span> Low financial risk based on your current data.
              </p>
            )}
            <div className="mt-4 flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Risk Score:</span>
              <span className={cn(
                "text-sm font-mono font-semibold",
                mlDisplayResults.multi_task_model?.risk_score > 0.5 ? "text-destructive" : "text-success"
              )}>
                {formatNumber(safeNumber(mlDisplayResults.multi_task_model?.risk_score) * 100, 1)}%
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Recommended Action */}
        <Card className="animate-fade-in stagger-8 card-hover gradient-border bg-primary/5">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <CardTitle className="font-display text-base">AI Recommendation</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground">
              Focus on reducing <span className="font-semibold text-primary">{highestNonEssentialExpense}</span> expenses.
              Potential savings of <span className="font-mono font-semibold text-primary">
                ${formatNumber(mlDisplayResults.multi_task_model?.recommended_savings_amount)}
              </span> possible.
            </p>
            <div className="mt-4 pt-3 border-t border-border/50">
              <p className="text-[11px] text-muted-foreground flex items-center gap-1">
                <Brain className="h-3 w-3" />
                AI-generated personalized suggestion
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard