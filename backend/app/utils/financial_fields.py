"""
Shared financial field definitions used across backend routes and repositories.
"""

OCCUPATION_MAPPING = {
    'Employed': 'Salaried',
    'Self_Employed': 'Self_Employed',
    'Student': 'Student',
    'Retired': 'Retired',
    'Salaried': 'Salaried',
}

EXPENSE_FIELDS = [
    'Rent',
    'Loan_Repayment',
    'Insurance',
    'Groceries',
    'Transport',
    'Eating_Out',
    'Entertainment',
    'Utilities',
    'Healthcare',
    'Education',
    'Miscellaneous',
]

VARIABLE_EXPENSE_FIELDS = [
    'Groceries',
    'Transport',
    'Eating_Out',
    'Entertainment',
    'Utilities',
    'Healthcare',
    'Education',
    'Miscellaneous',
]

TREND_EXPENSE_FIELDS = [
    'Rent',
    'Groceries',
    'Utilities',
    'Transport',
    'Insurance',
    'Eating_Out',
    'Healthcare',
    'Entertainment',
    'Miscellaneous',
]
