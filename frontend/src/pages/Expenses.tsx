
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Car, Home, Utensils, Gamepad2, Heart, GraduationCap, IndianRupeeIcon, MoreHorizontal, Loader2, Shield } from "lucide-react"
import { useUserData } from "@/hooks/useUserData"

const Expenses = () => {
  const { data: userData, isLoading: loading, error } = useUserData()

  if (loading) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading expense data...</span>
        </div>
      </div>
    )
  }
  if (error || !userData || !userData.predictions || userData.predictions.length === 0) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Failed to load expense data. Please try again.</p>
        </div>
      </div>
    )
  }

  // Get the latest prediction's input data
  const latestPrediction = userData.predictions[userData.predictions.length - 1]
  const userInput = latestPrediction.input

  // Convert user data to expense categories format
  const expenseCategories = [
    {
      name: 'Rent',
      amount: userInput.Rent || 0,
      percentage: ((userInput.Rent || 0) / (userInput.Income || 1)) * 100,
      icon: Home,
      color: 'bg-blue-500',
      isEssential: true,
      trend: 'stable',
      potentialSavings: 0
    },
    {
      name: 'Groceries',
      amount: userInput.Groceries || 0,
      percentage: ((userInput.Groceries || 0) / (userInput.Income || 1)) * 100,
      icon: ShoppingCart,
      color: 'bg-green-500',
      isEssential: true,
      trend: 'up',
      potentialSavings: userInput.Potential_Savings_Groceries || 0
    },
    {
      name: 'Utilities',
      amount: userInput.Utilities || 0,
      percentage: ((userInput.Utilities || 0) / (userInput.Income || 1)) * 100,
      icon: DollarSign,
      color: 'bg-yellow-500',
      isEssential: true,
      trend: 'down',
      potentialSavings: userInput.Potential_Savings_Utilities || 0
    },
    {
      name: 'Transport',
      amount: userInput.Transport || 0,
      percentage: ((userInput.Transport || 0) / (userInput.Income || 1)) * 100,
      icon: Car,
      color: 'bg-purple-500',
      isEssential: false,
      trend: 'up',
      potentialSavings: userInput.Potential_Savings_Transport || 0
    },
    {
      name: 'Healthcare',
      amount: userInput.Healthcare || 0,
      percentage: ((userInput.Healthcare || 0) / (userInput.Income || 1)) * 100,
      icon: Heart,
      color: 'bg-pink-500',
      isEssential: true,
      trend: 'stable',
      potentialSavings: userInput.Potential_Savings_Healthcare || 0
    },
    {
      name: 'Entertainment',
      amount: userInput.Entertainment || 0,
      percentage: ((userInput.Entertainment || 0) / (userInput.Income || 1)) * 100,
      icon: Gamepad2,
      color: 'bg-indigo-500',
      isEssential: false,
      trend: 'up',
      potentialSavings: userInput.Potential_Savings_Entertainment || 0
    },
    {
      name: 'Eating Out',
      amount: userInput.Eating_Out || 0,
      percentage: ((userInput.Eating_Out || 0) / (userInput.Income || 1)) * 100,
      icon: Utensils,
      color: 'bg-orange-500',
      isEssential: false,
      trend: 'up',
      potentialSavings: userInput.Potential_Savings_Eating_Out || 0
    },
    {
      name: 'Education',
      amount: userInput.Education || 0,
      percentage: ((userInput.Education || 0) / (userInput.Income || 1)) * 100,
      icon: GraduationCap,
      color: 'bg-indigo-500',
      isEssential: true,
      trend: 'stable',
      potentialSavings: userInput.Potential_Savings_Education || 0
    },
    {
      name: 'Miscellaneous',
      amount: userInput.Miscellaneous || 0,
      percentage: ((userInput.Miscellaneous || 0) / (userInput.Income || 1)) * 100,
      icon: MoreHorizontal,
      color: 'bg-gray-500',
      isEssential: false,
      trend: 'stable',
      potentialSavings: userInput.Potential_Savings_Miscellaneous || 0
    },
    {
      name: 'Insurance',
      amount: userInput.Insurance || 0,
      percentage: ((userInput.Insurance || 0) / (userInput.Income || 1)) * 100,
      icon: Shield,
      color: 'bg-red-500',
      isEssential: true,
      trend: 'stable',
      potentialSavings: 0
    },
  ].filter(category => category.amount > 0) // Only show categories with expenses

  const totalExpenses = expenseCategories.reduce((sum, cat) => sum + cat.amount, 0)
  const totalPotentialSavings = expenseCategories.reduce((sum, cat) => sum + cat.potentialSavings, 0)
  const essentialExpenses = expenseCategories.filter(cat => cat.isEssential).reduce((sum, cat) => sum + cat.amount, 0)
  const nonEssentialExpenses = expenseCategories.filter(cat => !cat.isEssential).reduce((sum, cat) => sum + cat.amount, 0)

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Expense Management</h1>
        <p className="text-muted-foreground">
          Track, analyze, and optimize your monthly spending patterns
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
            <IndianRupeeIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold">₹{totalExpenses.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {((totalExpenses / (userInput.Income || 1)) * 100).toFixed(1)}% of total income
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Essential Expenses</CardTitle>
            <Home className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold">₹{essentialExpenses.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {totalExpenses > 0 ? ((essentialExpenses / totalExpenses) * 100).toFixed(1) : 0}% of total expenses
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Non-Essential</CardTitle>
            <Gamepad2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold">₹{nonEssentialExpenses.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {totalExpenses > 0 ? ((nonEssentialExpenses / totalExpenses) * 100).toFixed(1) : 0}% of total expenses
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Savings Potential</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>            <div className="text-2xl font-bold text-success">₹{totalPotentialSavings.toLocaleString()}</div>
            <p className="text-xs text-success">
              {totalExpenses > 0 ? ((totalPotentialSavings / totalExpenses) * 100).toFixed(1) : 0}% optimization possible
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Expense Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Expense Categories</CardTitle>
            <CardDescription>Monthly spending breakdown by category</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {expenseCategories.map((category, index) => {
              const IconComponent = category.icon
              return (
                <div key={index} className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${category.color}`}>
                      <IconComponent className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{category.name}</span>
                        {category.isEssential && (
                          <Badge variant="outline" className="text-xs">Essential</Badge>
                        )}
                      </div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-sm text-muted-foreground">
                          {category.percentage.toFixed(1)}% of total
                        </span>
                        {category.trend === 'up' && <TrendingUp className="h-3 w-3 text-destructive" />}
                        {category.trend === 'down' && <TrendingDown className="h-3 w-3 text-success" />}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">₹{category.amount.toLocaleString()}</div>
                    {category.potentialSavings > 0 && (
                      <div className="text-xs text-success">
                        Save ₹{category.potentialSavings.toFixed(0)}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Optimization Suggestions */}
        <Card>
          <CardHeader>
            <CardTitle>Optimization Suggestions</CardTitle>
            <CardDescription>AI-powered recommendations to reduce expenses</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-success/10 border border-success/20">
              <div className="flex items-start space-x-3">
                <ShoppingCart className="h-5 w-5 text-success mt-1" />
                <div>
                  <h4 className="font-semibold text-success">Groceries Optimization</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Potential savings: ₹1,686/month. Try meal planning, bulk buying, and using coupons.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 border-success text-success hover:bg-success hover:text-white">
                    View Tips
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
              <div className="flex items-start space-x-3">
                <DollarSign className="h-5 w-5 text-warning mt-1" />
                <div>
                  <h4 className="font-semibold text-warning">Utilities Reduction</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Potential savings: ₹678/month. Consider energy-efficient appliances and smart usage.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 border-warning text-warning hover:bg-warning hover:text-white">
                    Learn More
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-start space-x-3">
                <Utensils className="h-5 w-5 text-info mt-1" />
                <div>
                  <h4 className="font-semibold text-info">Dining Out Alternative</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Potential savings: ₹466/month. Try cooking at home more often and limit restaurant visits.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 border-info text-info hover:bg-info hover:text-white">
                    Get Recipes
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-purple-100 border border-purple-200 dark:bg-purple-900/20 dark:border-purple-800">
              <div className="flex items-start space-x-3">
                <Car className="h-5 w-5 text-purple-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-purple-600">Transportation Savings</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Potential savings: ₹329/month. Consider carpooling, public transport, or remote work options.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white">
                    Explore Options
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Tracking */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Budget Progress</CardTitle>
          <CardDescription>Track your spending against budget limits</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {expenseCategories.slice(0, 6).map((category, index) => {
              const budgetLimit = category.amount * 1.1 // 10% buffer
              const spentPercentage = (category.amount / budgetLimit) * 100
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{category.name}</span>
                    <span className="text-muted-foreground">
                      {category.amount.toLocaleString()} / {budgetLimit.toLocaleString()}
                    </span>
                  </div>
                  <Progress 
                    value={spentPercentage} 
                    className={`h-2 ${spentPercentage > 90 ? 'bg-destructive/20' : spentPercentage > 75 ? 'bg-warning/20' : 'bg-success/20'}`}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{spentPercentage.toFixed(0)}% used</span>
                    <Badge 
                      variant={spentPercentage > 90 ? 'destructive' : spentPercentage > 75 ? 'secondary' : 'outline'}
                      className="text-xs"
                    >
                      {spentPercentage > 90 ? 'Over Budget' : spentPercentage > 75 ? 'Near Limit' : 'On Track'}
                    </Badge>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Expenses
