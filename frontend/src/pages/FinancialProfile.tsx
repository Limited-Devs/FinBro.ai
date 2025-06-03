
import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Slider } from "@/components/ui/slider"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { User, DollarSign, Home, Car, Utensils, Heart, GraduationCap } from "lucide-react"

const formSchema = z.object({
  income: z.number().min(0, "Income must be positive"),
  age: z.number().min(18, "Age must be at least 18").max(100, "Age must be realistic"),
  dependents: z.number().min(0, "Dependents cannot be negative"),
  occupation: z.string().min(1, "Please select an occupation"),
  cityTier: z.string().min(1, "Please select a city tier"),
  rent: z.number().min(0, "Rent must be positive"),
  loanRepayment: z.number().min(0, "Loan repayment cannot be negative"),
  insurance: z.number().min(0, "Insurance cannot be negative"),
  groceries: z.number().min(0, "Groceries cannot be negative"),
  transport: z.number().min(0, "Transport cannot be negative"),
  eatingOut: z.number().min(0, "Eating out cannot be negative"),
  entertainment: z.number().min(0, "Entertainment cannot be negative"),
  utilities: z.number().min(0, "Utilities cannot be negative"),
  healthcare: z.number().min(0, "Healthcare cannot be negative"),
  education: z.number().min(0, "Education cannot be negative"),
  miscellaneous: z.number().min(0, "Miscellaneous cannot be negative"),
  desiredSavingsPercentage: z.number().min(0, "Savings percentage cannot be negative").max(100, "Savings percentage cannot exceed 100"),
})

type FormData = z.infer<typeof formSchema>

const FinancialProfile = () => {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      income: 0,
      age: 30,
      dependents: 0,
      occupation: "",
      cityTier: "",
      rent: 0,
      loanRepayment: 0,
      insurance: 0,
      groceries: 0,
      transport: 0,
      eatingOut: 0,
      entertainment: 0,
      utilities: 0,
      healthcare: 0,
      education: 0,
      miscellaneous: 0,
      desiredSavingsPercentage: 10,
    },
  })

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    try {
      console.log("Form data submitted:", data)
      // Here you would send the data to your ML model API
      // const response = await fetch('/api/ml-model', { method: 'POST', body: JSON.stringify(data) })
      
      // For now, just log the data
      alert("Financial profile saved successfully!")
    } catch (error) {
      console.error("Error submitting form:", error)
      alert("Error saving profile. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto animate-fade-in">
      <div className="flex flex-col space-y-2 mb-6">
        <h1 className="text-3xl font-bold">Financial Profile</h1>
        <p className="text-muted-foreground">
          Help us understand your financial situation to provide personalized insights
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5 text-primary" />
                <span>Personal Information</span>
              </CardTitle>
              <CardDescription>Basic details about yourself</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="age"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Age</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="dependents"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Number of Dependents</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="occupation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Occupation</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select your occupation" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Self_Employed">Self Employed</SelectItem>
                        <SelectItem value="Employed">Employed</SelectItem>
                        <SelectItem value="Student">Student</SelectItem>
                        <SelectItem value="Retired">Retired</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="cityTier"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>City Tier</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select your city tier" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Tier_1">Tier 1 (Metro)</SelectItem>
                        <SelectItem value="Tier_2">Tier 2</SelectItem>
                        <SelectItem value="Tier_3">Tier 3</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Income Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-primary" />
                <span>Income & Savings</span>
              </CardTitle>
              <CardDescription>Your monthly income and savings goals</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="income"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Monthly Income (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="desiredSavingsPercentage"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Desired Savings Percentage: {field.value}%</FormLabel>
                    <FormControl>
                      <Slider
                        min={0}
                        max={50}
                        step={1}
                        value={[field.value]}
                        onValueChange={(value) => field.onChange(value[0])}
                        className="mt-2"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Housing & Fixed Expenses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Home className="h-5 w-5 text-primary" />
                <span>Housing & Fixed Expenses</span>
              </CardTitle>
              <CardDescription>Monthly housing and fixed costs</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="rent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rent/Mortgage (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="utilities"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Utilities (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="insurance"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Insurance (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="loanRepayment"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Loan Repayment (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Variable Expenses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Utensils className="h-5 w-5 text-primary" />
                <span>Variable Expenses</span>
              </CardTitle>
              <CardDescription>Monthly variable and lifestyle costs</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="groceries"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Groceries (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="transport"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Transport (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="eatingOut"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Eating Out (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="entertainment"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Entertainment (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="healthcare"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Healthcare (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="education"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Education (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="miscellaneous"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Miscellaneous (₹)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        {...field} 
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting} className="w-full md:w-auto">
              {isSubmitting ? "Saving..." : "Save Financial Profile"}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}

export default FinancialProfile
