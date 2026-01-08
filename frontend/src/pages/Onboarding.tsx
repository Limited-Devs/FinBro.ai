import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { User, DollarSign, Home, Utensils, ArrowRight, ArrowLeft, Loader2, CheckCircle2, Sparkles } from "lucide-react";
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { onboardingAPI } from '@/services/api';
import { formatNumber } from '@/services/utils';

const formSchema = z.object({
    // Personal Info
    Age: z.number().min(18, "Age must be at least 18").max(100, "Age must be realistic"),
    Dependents: z.number().min(0, "Dependents cannot be negative"),
    Occupation: z.string().min(1, "Please select an occupation"),
    City_Tier: z.string().min(1, "Please select a city tier"),

    // Income
    Income: z.number().min(1, "Income must be greater than 0"),
    Desired_Savings_Percentage: z.number().min(0).max(100),

    // Fixed Expenses
    Rent: z.number().min(0),
    Loan_Repayment: z.number().min(0),
    Insurance: z.number().min(0),
    Utilities: z.number().min(0),

    // Variable Expenses
    Groceries: z.number().min(0),
    Transport: z.number().min(0),
    Eating_Out: z.number().min(0),
    Entertainment: z.number().min(0),
    Healthcare: z.number().min(0),
    Education: z.number().min(0),
    Miscellaneous: z.number().min(0),
});

type FormData = z.infer<typeof formSchema>;

const STEPS = [
    { id: 1, title: "Personal Info", icon: User },
    { id: 2, title: "Income & Goals", icon: DollarSign },
    { id: 3, title: "Fixed Expenses", icon: Home },
    { id: 4, title: "Lifestyle Expenses", icon: Utensils },
];

const Onboarding = () => {
    const [currentStep, setCurrentStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();
    const { setOnboardingCompleted } = useAuth();

    const form = useForm<FormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            Age: 30,
            Dependents: 0,
            Occupation: "",
            City_Tier: "",
            Income: 0,
            Desired_Savings_Percentage: 20,
            Rent: 0,
            Loan_Repayment: 0,
            Insurance: 0,
            Utilities: 0,
            Groceries: 0,
            Transport: 0,
            Eating_Out: 0,
            Entertainment: 0,
            Healthcare: 0,
            Education: 0,
            Miscellaneous: 0,
        },
    });

    const progress = (currentStep / STEPS.length) * 100;

    const nextStep = async () => {
        // Validate current step fields
        let fieldsToValidate: (keyof FormData)[] = [];

        switch (currentStep) {
            case 1:
                fieldsToValidate = ['Age', 'Dependents', 'Occupation', 'City_Tier'];
                break;
            case 2:
                fieldsToValidate = ['Income', 'Desired_Savings_Percentage'];
                break;
            case 3:
                fieldsToValidate = ['Rent', 'Loan_Repayment', 'Insurance', 'Utilities'];
                break;
            case 4:
                fieldsToValidate = ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Healthcare', 'Education', 'Miscellaneous'];
                break;
        }

        const isValid = await form.trigger(fieldsToValidate);
        if (isValid && currentStep < STEPS.length) {
            setCurrentStep(currentStep + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    const onSubmit = async (data: FormData) => {
        setIsSubmitting(true);
        try {
            // Type assertion - form validation ensures all required fields are present
            await onboardingAPI.submit(data as any);

            // Update auth context
            setOnboardingCompleted(true);

            toast.success("Profile created successfully! Welcome to FinBro.ai");
            navigate('/dashboard');
        } catch (error: any) {
            console.error("Error submitting onboarding:", error);
            toast.error(error.message || "Failed to create profile. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const renderStepContent = () => {
        switch (currentStep) {
            case 1:
                return (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <FormField
                                control={form.control}
                                name="Age"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Age</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="30"
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
                                name="Dependents"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Number of Dependents</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="0"
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
                                name="Occupation"
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
                                                <SelectItem value="Employed">Employed</SelectItem>
                                                <SelectItem value="Self_Employed">Self Employed</SelectItem>
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
                                name="City_Tier"
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
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="space-y-6">
                        <FormField
                            control={form.control}
                            name="Income"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Monthly Income ($)</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="number"
                                            placeholder="5000"
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
                            name="Desired_Savings_Percentage"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Desired Savings: {field.value}%</FormLabel>
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
                                    <p className="text-sm text-muted-foreground mt-2">
                                        Based on your income, that's ${formatNumber((form.watch('Income') || 0) * field.value / 100)}/month
                                    </p>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                );

            case 3:
                return (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <FormField
                                control={form.control}
                                name="Rent"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Rent/Mortgage ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="1500"
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
                                name="Utilities"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Utilities ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="200"
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
                                name="Insurance"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Insurance ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="300"
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
                                name="Loan_Repayment"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Loan Repayment ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="0"
                                                {...field}
                                                onChange={(e) => field.onChange(Number(e.target.value))}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                );

            case 4:
                return (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <FormField
                                control={form.control}
                                name="Groceries"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Groceries ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="400"
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
                                name="Transport"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Transport ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="200"
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
                                name="Eating_Out"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Eating Out ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="150"
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
                                name="Entertainment"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Entertainment ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="100"
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
                                name="Healthcare"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Healthcare ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="50"
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
                                name="Education"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Education ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="0"
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
                                name="Miscellaneous"
                                render={({ field }) => (
                                    <FormItem className="md:col-span-2">
                                        <FormLabel>Miscellaneous ($)</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                placeholder="100"
                                                {...field}
                                                onChange={(e) => field.onChange(Number(e.target.value))}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="w-full max-w-2xl">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-4">
                        <Sparkles className="h-8 w-8 text-primary" />
                        <h1 className="text-3xl font-bold font-display">Welcome to FinBro.ai</h1>
                    </div>
                    <p className="text-muted-foreground">
                        Let's set up your financial profile to get personalized AI insights
                    </p>
                </div>

                {/* Progress */}
                <div className="mb-8">
                    <Progress value={progress} className="h-2 mb-4" />
                    <div className="flex justify-between">
                        {STEPS.map((step) => {
                            const Icon = step.icon;
                            const isActive = currentStep === step.id;
                            const isCompleted = currentStep > step.id;

                            return (
                                <div
                                    key={step.id}
                                    className={`flex flex-col items-center text-xs ${isActive ? 'text-primary' : isCompleted ? 'text-success' : 'text-muted-foreground'
                                        }`}
                                >
                                    <div className={`h-10 w-10 rounded-full flex items-center justify-center mb-1 ${isActive ? 'bg-primary/10 border-2 border-primary' :
                                        isCompleted ? 'bg-success/10' : 'bg-muted'
                                        }`}>
                                        {isCompleted ? (
                                            <CheckCircle2 className="h-5 w-5 text-success" />
                                        ) : (
                                            <Icon className="h-5 w-5" />
                                        )}
                                    </div>
                                    <span className="hidden sm:block">{step.title}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Form Card */}
                <Card className="shadow-xl border-2">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            {(() => {
                                const CurrentIcon = STEPS[currentStep - 1].icon;
                                return <CurrentIcon className="h-5 w-5 text-primary" />;
                            })()}
                            {STEPS[currentStep - 1].title}
                        </CardTitle>
                        <CardDescription>
                            {currentStep === 1 && "Tell us about yourself"}
                            {currentStep === 2 && "Share your income and savings goals"}
                            {currentStep === 3 && "Enter your fixed monthly expenses"}
                            {currentStep === 4 && "Enter your lifestyle and variable expenses"}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(onSubmit)}>
                                {renderStepContent()}

                                <div className="flex justify-between mt-8">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={prevStep}
                                        disabled={currentStep === 1}
                                    >
                                        <ArrowLeft className="h-4 w-4 mr-2" />
                                        Back
                                    </Button>

                                    {currentStep < STEPS.length ? (
                                        <Button type="button" onClick={nextStep}>
                                            Next
                                            <ArrowRight className="h-4 w-4 ml-2" />
                                        </Button>
                                    ) : (
                                        <Button type="submit" disabled={isSubmitting}>
                                            {isSubmitting ? (
                                                <>
                                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                    Creating Profile...
                                                </>
                                            ) : (
                                                <>
                                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                                    Complete Setup
                                                </>
                                            )}
                                        </Button>
                                    )}
                                </div>
                            </form>
                        </Form>
                    </CardContent>
                </Card>

                {/* Footer */}
                <p className="text-center text-xs text-muted-foreground mt-6">
                    Your data is securely stored and processed by our AI models to provide personalized financial insights.
                </p>
            </div>
        </div>
    );
};

export default Onboarding;
