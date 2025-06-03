
export interface UserData {
  predictions: Prediction[];
}

export interface Prediction {
  timestamp: string;
  input: PredictionInput;
  output: PredictionOutput;
}

export interface PredictionInput {
  Income: number;
  Age: number;
  Dependents: number;
  Occupation: string;
  City_Tier: string;
  Rent: number;
  Loan_Repayment: number;
  Insurance: number;
  Groceries: number;
  Transport: number;
  Eating_Out: number;
  Entertainment: number;
  Utilities: number;
  Healthcare: number;
  Education: number;
  Miscellaneous: number;
  Desired_Savings_Percentage: number;
  Disposable_Income: number;
  Potential_Savings_Groceries: number;
  Potential_Savings_Transport: number;
  Potential_Savings_Eating_Out: number;
  Potential_Savings_Entertainment: number;
  Potential_Savings_Utilities: number;
  Potential_Savings_Healthcare: number;
  Potential_Savings_Education: number;
  Potential_Savings_Miscellaneous: number;
  Savings_Rate: number;
  Actual_Savings_Potential: number;
  Essential_Expenses: number;
  Essential_Expense_Ratio: number;
  Non_Essential_Income: number;
  Expense_Efficiency: number;
  Total_Expenses: number;
  Debt_to_Income_Ratio: number;
  Financial_Stress_Score: number;
  Occupation_Retired: number;
  Occupation_Self_Employed: number;
  Occupation_Student: number;
  City_Tier_Tier_2: number;
  City_Tier_Tier_3: number;
  Age_Group_Mid_Career: number;
  Age_Group_Pre_Retirement: number;
  Age_Group_Senior: number;
  Age_Group_Young_Adult: number;
  Income_Bracket_Low_Income: number;
  Income_Bracket_Lower_Mid: number;
  Income_Bracket_Middle: number;
  Income_Bracket_Upper_Mid: number;
  Savings_Difficulty_Moderate: number;
  Savings_Difficulty_Very_Hard: number;
  Savings_Difficulty_nan: number;
}

export interface PredictionOutput {
  savings_model: {
    can_achieve_savings: boolean;
    confidence: number;
  };
  amount_model: {
    recommended_savings: number;
  };
  multi_task_model: {
    can_achieve_savings: boolean;
    savings_confidence: number;
    recommended_savings_amount: number;
    financial_risk: boolean;
    risk_score: number;
  };
}

export interface ChatMessage {
  message: string;
}

export interface ChatResponse {
  response: string;
}
