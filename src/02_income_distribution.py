import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. Configuration & Loading
# ==========================================
file_path = './data/CensusProfile2021-ProfilRecensement2021-20260205015247.csv'
output_dir = './results'
output_image = os.path.join(output_dir, 'income_distribution.png')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

print(f"Loading data from {file_path}...")
try:
    # Skip the first 3 rows
    df = pd.read_csv(file_path, skiprows=3, encoding='latin-1')
except FileNotFoundError:
    print(f"Error: Data file not found at {file_path}. Please check your folder structure.")
    exit()

# ==========================================
# 2. Complex Data Extraction (The Tricky Part)
# ==========================================
topic = 'Income of households in 2020'
df_income = df[df['Topic'] == topic].copy()

# Select and clean columns
df_income = df_income[['Characteristic', 'Total']]
df_income.columns = ['Income_Bin', 'Households']
df_income['Income_Bin'] = df_income['Income_Bin'].str.strip()

# --- [CORE CHALLENGE] ---
# We must manually define the bins to ensure logical sorting (not alphabetical).
# This prevents "$100k" from appearing before "$20k".
target_bins = [
    'Under $5,000',
    '$5,000 to $9,999',
    '$10,000 to $14,999',
    '$15,000 to $19,999',
    '$20,000 to $24,999',
    '$25,000 to $29,999',
    '$30,000 to $34,999',
    '$35,000 to $39,999',
    '$40,000 to $44,999',
    '$45,000 to $49,999',
    '$50,000 to $59,999',
    '$60,000 to $69,999',
    '$70,000 to $79,999',
    '$80,000 to $89,999',
    '$90,000 to $99,999',
    '$100,000 and over'
]

# Extract rows matching these bins
df_dist = df_income[df_income['Income_Bin'].isin(target_bins)].copy()

# --- [CRITICAL LOGIC FIX] ---
# Issue: The dataset lists these bins TWICE (once for "Total Income", once for "After-tax Income").
# They share identical labels, leading to double-counting if naive filtering is used.
# Fix: We keep only the first occurrence (Total Income) and drop duplicates.
df_dist = df_dist.drop_duplicates(subset=['Income_Bin'], keep='first')

# Enforce logical sorting order using reindex
df_dist = df_dist.set_index('Income_Bin').reindex(target_bins).reset_index()

# Convert counts to numeric
df_dist['Households'] = pd.to_numeric(df_dist['Households'], errors='coerce')

# ==========================================
# 3. Data Insights Calculation
# ==========================================
total_households = df_dist['Households'].sum()

# Define "Low Income" as < $40,000 for this analysis
low_income_bins = target_bins[:8] # The first 8 bins cover $0 - $39,999
low_income_count = df_dist[df_dist['Income_Bin'].isin(low_income_bins)]['Households'].sum()
high_income_count = df_dist[df_dist['Income_Bin'] == '$100,000 and over']['Households'].sum()

low_ratio = (low_income_count / total_households) * 100
high_ratio = (high_income_count / total_households) * 100

print(f"Total Households Analyzed: {total_households}")
print(f"Low Income (<$40k): {low_ratio:.1f}%")
print(f"High Income (>$100k): {high_ratio:.1f}%")

# ==========================================
# 4. Visualization
# ==========================================
plt.figure(figsize=(14, 8))
# Use Teal color with black edges for better visibility
bars = plt.bar(df_dist['Income_Bin'], df_dist['Households'], color='#008080', edgecolor='black', alpha=0.8)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 5,
             f'{int(height)}',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.title('Household Total Income Distribution (2020)\nMetro Vancouver A', fontsize=16)
plt.xlabel('Income Brackets', fontsize=12)
plt.ylabel('Number of Households', fontsize=12)
plt.xticks(rotation=45, ha='right') # Rotate labels to prevent overlap
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig(output_image)
print(f"Chart saved successfully to {output_image}")