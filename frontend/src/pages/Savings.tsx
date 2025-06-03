
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Target, TrendingUp, DollarSign, Calendar, AlertCircle, CheckCircle2, Clock, Loader2 } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { useUserData } from "@/hooks/useUserData"

const Savings = () => {
  const { data: userData, isLoading: loading, error } = useUserData()

  if (loading) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading savings data...</span>
        </div>
      </div>
    )
  }
  if (error || !userData || !userData.predictions || userData.predictions.length === 0) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Failed to load savings data. Please try again.</p>
        </div>
      </div>
    )
  }

  // Get the latest prediction's input and output data
  const latestPrediction = userData.predictions[userData.predictions.length - 1]
  const userInput = latestPrediction.input
  const userOutput = latestPrediction.output

  // Calculate dynamic savings goals based on user data
  const monthlySavingsAmount = (userInput.Income || 0) * (userInput.Savings_Rate || 0.10)
  const emergencyFundTarget = (userInput.Income || 0) * 6 // 6 months of income
  const currentSavings = userInput.Disposable_Income || 0

  const savingsGoals = [
    {
      id: 1,
      name: 'Emergency Fund',
      target: emergencyFundTarget,
      current: currentSavings * 0.5, // Assume 50% is in emergency fund
      deadline: '2025-12-31',
      priority: 'high',
      status: 'in_progress',
      monthlyContribution: monthlySavingsAmount * 0.4, // 40% of savings to emergency
      category: 'safety'
    },    {
      id: 2,
      name: 'Investment Portfolio',
      target: (userInput.Income || 0) * 24, // 2 years of income as investment target
      current: currentSavings * 0.3, // Assume 30% is in investments
      deadline: '2026-06-30',
      priority: 'medium',
      status: 'in_progress',
      monthlyContribution: monthlySavingsAmount * 0.35, // 35% to investments
      category: 'growth'
    },
    {
      id: 3,
      name: 'Vacation Fund',
      target: (userInput.Income || 0) * 0.5, // Half month income for vacation
      current: currentSavings * 0.1, // Assume 10% for vacation
      deadline: '2025-07-01',
      priority: 'low',
      status: 'in_progress',
      monthlyContribution: monthlySavingsAmount * 0.15, // 15% to vacation
      category: 'lifestyle'
    },
    {
      id: 4,
      name: 'Home Improvement',
      target: (userInput.Income || 0) * 1.5, // 1.5 months income for home improvement
      current: currentSavings * 0.1, // Assume 10% for home improvement
      deadline: '2026-12-31',
      priority: 'medium',
      status: 'planning',
      monthlyContribution: monthlySavingsAmount * 0.1, // 10% to home improvement
      category: 'home'
    }
  ]

  // Generate projection data based on current savings and monthly contributions
  const savingsProjection = Array.from({ length: 6 }, (_, i) => {
    const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][i]
    return {
      month,
      emergency: Math.max(0, savingsGoals[0].current + (savingsGoals[0].monthlyContribution * (i + 1))),
      investment: Math.max(0, savingsGoals[1].current + (savingsGoals[1].monthlyContribution * (i + 1))),
      vacation: Math.max(0, savingsGoals[2].current + (savingsGoals[2].monthlyContribution * (i + 1))),
      home: Math.max(0, savingsGoals[3].current + (savingsGoals[3].monthlyContribution * (i + 1))),
    }
  })
  // AI recommendations based on user data
  const aiRecommendations = [
    {
      title: 'Optimize Emergency Fund',
      description: `Based on your income of ₹${userInput.Income?.toLocaleString()}, build an emergency fund of ₹${emergencyFundTarget.toLocaleString()}.`,
      impact: 'High',
      timeframe: '12 months',
      action: `Increase monthly contribution by ₹${Math.max(0, (emergencyFundTarget - savingsGoals[0].current) / 12 - savingsGoals[0].monthlyContribution).toFixed(0)}`
    },
    {
      title: 'Diversify Investment Strategy',
      description: 'With your current savings rate, you can achieve better returns through diversified investments.',
      impact: 'Medium',
      timeframe: '6 months',
      action: 'Allocate 60% to index funds, 40% to bonds'
    },
    {
      title: 'Automate Savings',
      description: `Set up automatic transfers for ₹${monthlySavingsAmount.toFixed(0)} monthly to improve consistency.`,
      impact: 'Medium',
      timeframe: '1 month',
      action: 'Setup automatic transfers for different goals'
    }
  ]

  const totalSavingsTarget = savingsGoals.reduce((sum, goal) => sum + goal.target, 0)
  const totalCurrentSavings = savingsGoals.reduce((sum, goal) => sum + goal.current, 0)
  const overallProgress = totalSavingsTarget > 0 ? (totalCurrentSavings / totalSavingsTarget) * 100 : 0

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-success'
      case 'in_progress': return 'text-primary'
      case 'planning': return 'text-warning'
      case 'paused': return 'text-muted-foreground'
      default: return 'text-muted-foreground'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle2
      case 'in_progress': return Clock
      case 'planning': return Target
      case 'paused': return AlertCircle
      default: return Clock
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-destructive'
      case 'medium': return 'bg-warning'
      case 'low': return 'bg-success'
      default: return 'bg-muted'
    }
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Savings Goals</h1>
        <p className="text-muted-foreground">
          Track your progress and optimize your savings strategy with AI insights
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{totalCurrentSavings.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {overallProgress.toFixed(1)}% of total goals
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Savings</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold">₹{monthlySavingsAmount.toLocaleString()}</div>
            <p className="text-xs text-success">
              {userInput.Income > 0 ? ((monthlySavingsAmount / userInput.Income) * 100).toFixed(1) : 0}% of income saved
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Goals</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{savingsGoals.filter(g => g.status === 'in_progress').length}</div>
            <p className="text-xs text-muted-foreground">
              out of {savingsGoals.length} total goals
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Confidence</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold text-success">{userOutput.savings_model.confidence ? (userOutput.savings_model.confidence * 100).toFixed(1) : '99.9'}%</div>
            <p className="text-xs text-success">
              Goals achievable
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Savings Goals List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Savings Goals</CardTitle>
            <CardDescription>Track progress towards your financial objectives</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {savingsGoals.map((goal) => {
              const progressPercentage = (goal.current / goal.target) * 100
              const StatusIcon = getStatusIcon(goal.status)
              const monthsToGoal = goal.target > goal.current ? Math.ceil((goal.target - goal.current) / goal.monthlyContribution) : 0
              
              return (
                <div key={goal.id} className="p-4 rounded-lg border hover:bg-muted/50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getPriorityColor(goal.priority)}`}></div>
                      <div>
                        <h4 className="font-semibold">{goal.name}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <StatusIcon className={`h-4 w-4 ${getStatusColor(goal.status)}`} />
                          <span className={`text-xs capitalize ${getStatusColor(goal.status)}`}>
                            {goal.status.replace('_', ' ')}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {goal.priority} priority
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">
                        ₹{goal.current.toLocaleString()} / ₹{goal.target.toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {monthsToGoal > 0 ? `₹${monthsToGoal} months left` : 'Goal achieved!'}
                      </div>
                    </div>
                  </div>
                  
                  <Progress value={progressPercentage} className="h-2 mb-2" />
                  
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{progressPercentage.toFixed(1)}% complete</span>
                    <span>₹{goal.monthlyContribution.toLocaleString()}/month</span>
                  </div>
                </div>
              )
            })}
            
            <Button className="w-full" variant="outline">
              <Target className="h-4 w-4 mr-2" />
              Add New Goal
            </Button>
          </CardContent>
        </Card>

        {/* Savings Projection */}
        <Card>
          <CardHeader>
            <CardTitle>Savings Projection</CardTitle>
            <CardDescription>Projected growth of your savings goals over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={savingsProjection}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="month" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => [`₹${Number(value).toLocaleString()}`, '']}
                />
                <Line type="monotone" dataKey="emergency" stroke="#EF4444" strokeWidth={2} />
                <Line type="monotone" dataKey="investment" stroke="#10B981" strokeWidth={2} />
                <Line type="monotone" dataKey="vacation" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="home" stroke="#F59E0B" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>AI-Powered Recommendations</CardTitle>
          <CardDescription>Personalized suggestions to optimize your savings strategy</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {aiRecommendations.map((rec, index) => (
              <div key={index} className="p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-semibold">{rec.title}</h4>
                  <Badge variant={rec.impact === 'High' ? 'destructive' : rec.impact === 'Medium' ? 'secondary' : 'outline'}>
                    {rec.impact} Impact
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {rec.description}
                </p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-xs">
                    <Calendar className="h-3 w-3" />
                    <span>Timeline: {rec.timeframe}</span>
                  </div>
                  <div className="text-xs font-medium text-primary">
                    Action: {rec.action}
                  </div>
                </div>
                <Button size="sm" className="w-full mt-3">
                  Implement
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Savings
