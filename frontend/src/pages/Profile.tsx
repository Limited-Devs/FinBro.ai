
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { User, Edit, Save, Shield, Bell, CreditCard, Target, TrendingUp, Loader2 } from "lucide-react"
import { useState } from "react"
import { useUserData } from "@/hooks/useUserData"

const Profile = () => {
  const { data: userData, isLoading: loading, error } = useUserData()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: "John Smith",
    email: "john.smith@email.com",
    phone: "+1 (555) 123-4567",
    income: 0,
    age: 0,
    dependents: 0,
    occupation: "",
    cityTier: "",
    savingsGoal: 0,
  })
  // Update form data when userData loads
  useState(() => {
    if (userData?.predictions?.[0]?.input) {
      const userInput = userData.predictions[0].input
      setFormData(prev => ({
        ...prev,
        income: userInput.Income || 0,
        age: userInput.Age || 0,
        dependents: userInput.Dependents || 0,
        occupation: userInput.Occupation || "",
        cityTier: userInput.City_Tier || "",
        savingsGoal: userInput.Desired_Savings_Percentage || 0,
      }))
    }
  })

  if (loading) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading profile data...</span>
        </div>
      </div>
    )
  }

  if (error || !userData) {
    return (
      <div className="p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Failed to load profile data. Please try again.</p>
        </div>
      </div>
    )
  }
  const handleSave = () => {
    setIsEditing(false)
    // Here you would typically save to your backend/Supabase
    console.log('Saving profile data:', formData)
  }  // Calculate financial health based on real user data
  const userInput = userData?.predictions?.[0]?.input
  const userOutput = userData?.predictions?.[0]?.output
  
  const financialHealth = {
    score: userOutput?.multi_task_model?.risk_score ? 
           Math.round((1 - userOutput.multi_task_model.risk_score) * 100) : 
           Math.round((1 - (userInput?.Financial_Stress_Score || 0)) * 100),
    factors: [
      { 
        name: 'Income Stability', 
        score: userInput?.Occupation === 'Employed' ? 85 : userInput?.Occupation === 'Self_Employed' ? 70 : 60, 
        status: userInput?.Occupation === 'Employed' ? 'good' : 'average' 
      },
      { 
        name: 'Savings Rate', 
        score: Math.min(100, (userInput?.Savings_Rate || 0) * 500), // Scale 0.2 savings rate to ~100 score
        status: (userInput?.Savings_Rate || 0) > 0.15 ? 'good' : (userInput?.Savings_Rate || 0) > 0.10 ? 'average' : 'needs_improvement' 
      },
      { 
        name: 'Expense Management', 
        score: Math.max(0, 100 - (userInput?.Financial_Stress_Score || 0) * 100), 
        status: (userInput?.Financial_Stress_Score || 0) < 0.3 ? 'good' : (userInput?.Financial_Stress_Score || 0) < 0.6 ? 'average' : 'critical' 
      },
      { 
        name: 'Emergency Fund', 
        score: Math.min(100, ((userInput?.Actual_Savings_Potential || 0) / (userInput?.Income || 1)) * 20), // Based on savings potential
        status: ((userInput?.Actual_Savings_Potential || 0) / (userInput?.Income || 1)) > 0.5 ? 'good' : ((userInput?.Actual_Savings_Potential || 0) / (userInput?.Income || 1)) > 0.3 ? 'average' : 'critical' 
      },
      { 
        name: 'Investment Portfolio', 
        score: userOutput?.multi_task_model?.can_achieve_savings ? 75 : 25, // Based on ML prediction
        status: userOutput?.multi_task_model?.can_achieve_savings ? 'good' : 'critical' 
      },
    ]
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success'
    if (score >= 60) return 'text-warning'
    return 'text-destructive'
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'good': return <Badge className="bg-success text-success-foreground">Good</Badge>
      case 'average': return <Badge variant="secondary">Average</Badge>
      case 'needs_improvement': return <Badge className="bg-warning text-warning-foreground">Needs Work</Badge>
      case 'critical': return <Badge variant="destructive">Critical</Badge>
      default: return <Badge variant="outline">Unknown</Badge>
    }
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Profile Settings</h1>
        <p className="text-muted-foreground">
          Manage your personal information and financial preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personal Information */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                <CardTitle>Personal Information</CardTitle>
              </div>
              <Button
                variant={isEditing ? "default" : "outline"}
                size="sm"
                onClick={isEditing ? handleSave : () => setIsEditing(true)}
              >
                {isEditing ? (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Profile
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="income">Monthly Income (₹)</Label>
                <Input
                  id="income"
                  type="number"
                  value={formData.income}
                  onChange={(e) => setFormData({...formData, income: parseFloat(e.target.value)})}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dependents">Dependents</Label>
                <Input
                  id="dependents"
                  type="number"
                  value={formData.dependents}
                  onChange={(e) => setFormData({...formData, dependents: parseInt(e.target.value)})}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="occupation">Occupation</Label>
                <Select value={formData.occupation} onValueChange={(value) => setFormData({...formData, occupation: value})} disabled={!isEditing}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Self_Employed">Self Employed</SelectItem>
                    <SelectItem value="Employed">Employed</SelectItem>
                    <SelectItem value="Student">Student</SelectItem>
                    <SelectItem value="Retired">Retired</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="cityTier">City Tier</Label>
                <Select value={formData.cityTier} onValueChange={(value) => setFormData({...formData, cityTier: value})} disabled={!isEditing}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Tier_1">Tier 1</SelectItem>
                    <SelectItem value="Tier_2">Tier 2</SelectItem>
                    <SelectItem value="Tier_3">Tier 3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="savingsGoal">Desired Savings Percentage (%)</Label>
              <Input
                id="savingsGoal"
                type="number"
                step="0.01"
                value={formData.savingsGoal}
                onChange={(e) => setFormData({...formData, savingsGoal: parseFloat(e.target.value)})}
                disabled={!isEditing}
              />
            </div>
          </CardContent>
        </Card>

        {/* Financial Health Score */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Financial Health
            </CardTitle>
            <CardDescription>Overall financial wellness assessment</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className={`text-4xl font-bold ${getScoreColor(financialHealth.score)}`}>
                {financialHealth.score}
              </div>
              <p className="text-sm text-muted-foreground">Overall Score</p>
            </div>

            <div className="space-y-3">
              {financialHealth.factors.map((factor, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{factor.name}</span>
                    {getStatusBadge(factor.status)}
                  </div>
                  <Progress value={factor.score} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{factor.score}/100</span>
                  </div>
                </div>
              ))}
            </div>

            <Button className="w-full" variant="outline">
              <Target className="h-4 w-4 mr-2" />
              Improve Score
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Settings Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Email Notifications</span>
              <Badge variant="outline">Enabled</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Goal Reminders</span>
              <Badge variant="outline">Enabled</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Spending Alerts</span>
              <Badge variant="outline">Enabled</Badge>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              Manage Preferences
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Two-Factor Auth</span>
              <Badge className="bg-success text-success-foreground">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Data Encryption</span>
              <Badge className="bg-success text-success-foreground">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Privacy Mode</span>
              <Badge variant="outline">Disabled</Badge>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              Security Settings
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CreditCard className="h-5 w-5 mr-2" />
              Connected Accounts
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Primary Bank</span>
              <Badge className="bg-success text-success-foreground">Connected</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Credit Cards</span>
              <Badge variant="secondary">2 Connected</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Investment Account</span>
              <Badge variant="outline">Not Connected</Badge>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              Manage Accounts
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Profile
