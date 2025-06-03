
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart, RadialBarChart, RadialBar, Legend } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Target, Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { useUserData } from '@/hooks/useUserData'

const Analytics = () => {
  const { data: userData, isLoading, error } = useUserData()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading analytics data...</span>
      </div>
    )
  }

  if (error || !userData?.predictions?.[0]) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold">Financial Analytics</h1>
          <p className="text-muted-foreground">
            Unable to load analytics data. Please check your connection.
          </p>
        </div>
      </div>
    )
  }

  const prediction = userData.predictions[0]
  const input = prediction.input
  const output = prediction.output

  // Calculate potential savings data from the API response
  const potentialSavingsData = [
    { 
      category: 'Groceries', 
      current: input.Groceries, 
      potential: input.Potential_Savings_Groceries, 
      savings: ((input.Potential_Savings_Groceries / input.Groceries) * 100).toFixed(1)
    },
    { 
      category: 'Utilities', 
      current: input.Utilities, 
      potential: input.Potential_Savings_Utilities, 
      savings: ((input.Potential_Savings_Utilities / input.Utilities) * 100).toFixed(1)
    },
    { 
      category: 'Eating Out', 
      current: input.Eating_Out, 
      potential: input.Potential_Savings_Eating_Out, 
      savings: ((input.Potential_Savings_Eating_Out / input.Eating_Out) * 100).toFixed(1)
    },
    { 
      category: 'Transport', 
      current: input.Transport, 
      potential: input.Potential_Savings_Transport, 
      savings: ((input.Potential_Savings_Transport / input.Transport) * 100).toFixed(1)
    },
    { 
      category: 'Entertainment', 
      current: input.Entertainment, 
      potential: input.Potential_Savings_Entertainment, 
      savings: ((input.Potential_Savings_Entertainment / input.Entertainment) * 100).toFixed(1)
    },
    { 
      category: 'Healthcare', 
      current: input.Healthcare, 
      potential: input.Potential_Savings_Healthcare, 
      savings: ((input.Potential_Savings_Healthcare / input.Healthcare) * 100).toFixed(1)
    },
    { 
      category: 'Miscellaneous', 
      current: input.Miscellaneous, 
      potential: input.Potential_Savings_Miscellaneous, 
      savings: ((input.Potential_Savings_Miscellaneous / input.Miscellaneous) * 100).toFixed(1)
    },
  ]

  const expenseEfficiencyData = [
    { name: 'Current Efficiency', value: input.Expense_Efficiency * 100, fill: '#10B981' },
    { name: 'Potential Improvement', value: (1 - input.Expense_Efficiency) * 100, fill: '#E5E7EB' },
  ]

  const financialHealthData = [
    { 
      metric: 'Savings Rate', 
      current: (input.Savings_Rate * 100).toFixed(1), 
      target: 20, 
      status: input.Savings_Rate >= 0.2 ? 'good' : 'below' 
    },
    { 
      metric: 'Emergency Fund', 
      current: ((input.Actual_Savings_Potential / input.Essential_Expenses) * 100).toFixed(1), 
      target: 100, 
      status: (input.Actual_Savings_Potential / input.Essential_Expenses) >= 1 ? 'good' : 'critical' 
    },
    { 
      metric: 'Debt Ratio', 
      current: (input.Debt_to_Income_Ratio * 100).toFixed(1), 
      target: 0, 
      status: input.Debt_to_Income_Ratio === 0 ? 'good' : 'below' 
    },
    { 
      metric: 'Investment Rate', 
      current: 0, 
      target: 15, 
      status: 'none' 
    },
  ]

  // Generate mock monthly trend data based on current data
  const monthlyTrendData = [
    { month: 'Jan', income: input.Income * 0.95, expenses: input.Total_Expenses * 0.98, savings: input.Actual_Savings_Potential * 0.9 },
    { month: 'Feb', income: input.Income * 1.02, expenses: input.Total_Expenses * 0.96, savings: input.Actual_Savings_Potential * 1.1 },
    { month: 'Mar', income: input.Income * 0.98, expenses: input.Total_Expenses * 1.01, savings: input.Actual_Savings_Potential * 0.8 },
    { month: 'Apr', income: input.Income * 1.05, expenses: input.Total_Expenses * 0.94, savings: input.Actual_Savings_Potential * 1.2 },
    { month: 'May', income: input.Income, expenses: input.Total_Expenses, savings: input.Actual_Savings_Potential },
    { month: 'Jun', income: input.Income * 1.03, expenses: input.Total_Expenses * 0.92, savings: input.Actual_Savings_Potential * 1.15 },
  ]

  const totalPotentialSavings = potentialSavingsData.reduce((sum, item) => sum + item.potential, 0)
  const savingsPercentage = ((totalPotentialSavings / input.Total_Expenses) * 100).toFixed(1)
  const highestSavingsCategory = potentialSavingsData.reduce((max, item) => 
    parseFloat(item.savings) > parseFloat(max.savings) ? item : max
  )

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Financial Analytics</h1>
        <p className="text-muted-foreground">
          Deep insights into your spending patterns and optimization opportunities
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Potential Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">₹{totalPotentialSavings.toFixed(0)}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                {savingsPercentage}% optimization possible
              </span>
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expense Efficiency</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(input.Expense_Efficiency * 100).toFixed(0)}%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-warning flex items-center">
                <TrendingDown className="h-3 w-3 mr-1" />
                Room for improvement
              </span>
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Highest Savings Category</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{highestSavingsCategory.category}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success">
                {highestSavingsCategory.savings}% potential reduction
              </span>
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Financial Stress</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning">{(input.Financial_Stress_Score * 100).toFixed(0)}%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success">
                {input.Financial_Stress_Score < 0.5 ? "Below average stress level" : "Above average stress"}
              </span>
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Potential Savings by Category */}
        <Card>
          <CardHeader>
            <CardTitle>Optimization Opportunities</CardTitle>
            <CardDescription>Potential savings by expense category</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={potentialSavingsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="category" 
                  stroke="#9CA3AF" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                  formatter={(value, name) => [
                    name === 'potential' ? `₹${value}` : `${value}%`,
                    name === 'potential' ? 'Potential Savings' : 'Savings %'
                  ]}
                />
                <Bar dataKey="potential" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Monthly Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Financial Trend</CardTitle>
            <CardDescription>Income, expenses, and savings over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={monthlyTrendData}>
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
                <Area type="monotone" dataKey="income" stackId="1" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="expenses" stackId="2" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} />
                <Area type="monotone" dataKey="savings" stackId="3" stroke="#10B981" fill="#10B981" fillOpacity={0.8} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Expense Efficiency */}
        <Card>
          <CardHeader>
            <CardTitle>Expense Efficiency Score</CardTitle>
            <CardDescription>How efficiently you're managing expenses</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={[{name: 'Efficiency', value: input.Expense_Efficiency * 100, fill: '#10B981'}]}>
                <RadialBar dataKey="value" cornerRadius={10} fill="#10B981" />
                <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="fill-foreground text-2xl font-bold">
                  {(input.Expense_Efficiency * 100).toFixed(0)}%
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="text-center mt-4">
              <Badge variant="outline" className={
                input.Expense_Efficiency >= 0.7 ? "text-success border-success" :
                input.Expense_Efficiency >= 0.4 ? "text-warning border-warning" :
                "text-destructive border-destructive"
              }>
                {input.Expense_Efficiency >= 0.7 ? "Excellent" :
                 input.Expense_Efficiency >= 0.4 ? "Needs Improvement" :
                 "Poor"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Financial Health Metrics */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Financial Health Scorecard</CardTitle>
            <CardDescription>Key metrics compared to recommended targets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {financialHealthData.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      item.status === 'good' ? 'bg-success' :
                      item.status === 'below' ? 'bg-warning' :
                      item.status === 'critical' ? 'bg-destructive' :
                      'bg-muted'
                    }`}></div>
                    <span className="font-medium">{item.metric}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">
                      {item.current}% / {item.target}%
                    </div>
                    <div className={`text-xs ${
                      item.status === 'good' ? 'text-success' :
                      item.status === 'below' ? 'text-warning' :
                      item.status === 'critical' ? 'text-destructive' :
                      'text-muted-foreground'
                    }`}>
                      {item.status === 'good' ? 'On Track' :
                       item.status === 'below' ? 'Below Target' :
                       item.status === 'critical' ? 'Needs Attention' :
                       'Not Started'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Analytics
