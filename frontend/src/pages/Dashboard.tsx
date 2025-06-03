import React, { useMemo } from 'react'; // Added React and useMemo
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, DollarSign, AlertTriangle, Zap } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsBarTooltip } from 'recharts'
import { useUserData } from '@/hooks/useUserData' // Import useUserData hook

const Dashboard = () => {
  const { data: userDataResponse, isLoading, error: queryError } = useUserData() // Use the hook

  // Derived states using useMemo for efficiency
  const latestPrediction = useMemo(() =>
    userDataResponse?.predictions?.[userDataResponse.predictions.length - 1],
    [userDataResponse]
  )

  const displayUserData = useMemo(() => latestPrediction?.input, [latestPrediction])
  const mlDisplayResults = useMemo(() => latestPrediction?.output, [latestPrediction])

  const expenseData = useMemo(() => {
    if (!displayUserData) return []
    return [
      { name: 'Rent', value: displayUserData.Rent || 0, color: '#8884d8' },
      { name: 'Groceries', value: displayUserData.Groceries || 0, color: '#82ca9d' },
      { name: 'Utilities', value: displayUserData.Utilities || 0, color: '#ffc658' },
      { name: 'Transport', value: displayUserData.Transport || 0, color: '#ff7300' },
      { name: 'Insurance', value: displayUserData.Insurance || 0, color: '#00ff00' },
      { name: 'Eating Out', value: displayUserData.Eating_Out || 0, color: '#ff0000' },
      { name: 'Healthcare', value: displayUserData.Healthcare || 0, color: '#8dd1e1' },
      { name: 'Entertainment', value: displayUserData.Entertainment || 0, color: '#d084d0' },
      { name: 'Miscellaneous', value: displayUserData.Miscellaneous || 0, color: '#87d068' },
    ].filter(expense => expense.value > 0)
  }, [displayUserData])

  // Static savings data (remains the same)
  const savingsData = [
    { month: 'Jan', actual: 2800, target: 3200 },
    { month: 'Feb', actual: 3100, target: 3200 },
    { month: 'Mar', actual: 2900, target: 3200 },
    { month: 'Apr', actual: 3400, target: 3200 },
    { month: 'May', actual: 3200, target: 3200 },
    { month: 'Jun', actual: 3500, target: 3200 },
  ]

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <p>Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  if (queryError) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center text-red-500">
            <AlertTriangle className="mx-auto h-12 w-12" />
            <p className="mt-2">Error loading dashboard data:</p>
            <p className="text-sm">{(queryError as Error).message}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!displayUserData || !mlDisplayResults) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <p>No financial data available to display.</p>
        </div>
      </div>
    )
  }

  const savingsGoalProgress = displayUserData.Actual_Savings_Potential && mlDisplayResults.amount_model.recommended_savings
    ? (displayUserData.Actual_Savings_Potential / mlDisplayResults.amount_model.recommended_savings) * 100
    : 0

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Financial Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's your financial overview for this month.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-primary/20 hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Income</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${displayUserData.Income?.toLocaleString() || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">Current monthly income</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${displayUserData.Actual_Savings_Potential?.toLocaleString() || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">Estimated based on your spending</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Savings Goal</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${mlDisplayResults.amount_model.recommended_savings?.toLocaleString() || 'N/A'}</div>
            <Progress value={savingsGoalProgress} className="mt-2 h-2" />
            <p className="text-xs text-muted-foreground mt-1">{savingsGoalProgress.toFixed(0)}% of AI recommended goal</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Financial Stress</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(displayUserData.Financial_Stress_Score * 100)?.toFixed(0) || 'N/A'}%</div>
            <p className="text-xs text-muted-foreground">Lower is better</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Expense Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={expenseData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {expenseData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Savings Progress (Last 6 Months)</CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={savingsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsBarTooltip />
                <Legend />
                <Bar dataKey="actual" fill="#8884d8" name="Actual Savings" />
                <Bar dataKey="target" fill="#82ca9d" name="Target Savings" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights - This section would also use mlDisplayResults */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>AI Savings Insight</CardTitle>
          </CardHeader>
          <CardContent>
            {mlDisplayResults.savings_model?.can_achieve_savings ? (
              <p className="text-green-600">Good news! Our AI indicates you can achieve your savings goals.</p>
            ) : (
              <p className="text-orange-600">Our AI suggests achieving your current savings goals might be challenging. Consider reviewing your expenses or goals.</p>
            )}
            <p className="text-sm text-muted-foreground mt-2">Confidence: {(mlDisplayResults.savings_model?.confidence * 100).toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>AI Financial Risk</CardTitle>
          </CardHeader>
          <CardContent>
            {mlDisplayResults.multi_task_model?.financial_risk ? (
              <p className="text-red-600">Our AI has identified a potential financial risk. It's advisable to review your financial situation.</p>
            ) : (
              <p className="text-green-600">Our AI indicates a low financial risk based on your current data.</p>
            )}
            <p className="text-sm text-muted-foreground mt-2">Risk Score: {(mlDisplayResults.multi_task_model?.risk_score * 100).toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>AI Recommended Action</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Consider focusing on reducing <span className="font-semibold">{/* TODO: Add dynamic suggestion, e.g., highest non-essential expense */}</span> expenses. Our AI suggests potential savings of <span className="font-semibold">${mlDisplayResults.multi_task_model?.recommended_savings_amount?.toLocaleString()}</span> are possible.</p>
            <p className="text-sm text-muted-foreground mt-2">This is an AI-generated suggestion.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard