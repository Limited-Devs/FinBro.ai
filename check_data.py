
import pandas as pd
df = pd.read_csv('data/data.csv')
print("Occupation unique values:", df['Occupation'].unique())
print("City_Tier unique values:", df['City_Tier'].unique())
