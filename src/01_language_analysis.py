import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. Configuration
# ==========================================
# Assuming script is in src/, data is in data/
file_path = './data/CensusProfile2021-ProfilRecensement2021-20260205015247.csv'
output_dir = './results'
output_image = os.path.join(output_dir, 'top5_languages.png')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 2. Data Loading & Initial Cleaning
# ==========================================
print(f"Loading data from {file_path}...")
try:
    # Skip the first 3 rows of metadata
    df = pd.read_csv(file_path, skiprows=3, encoding='latin-1')
except FileNotFoundError:
    print(f"Error: Data file not found at {file_path}. Please check your folder structure.")
    exit()

# Filter for the "Mother tongue" topic
df_lang = df[df['Topic'] == 'Mother tongue'].copy()

# Select relevant columns and rename for clarity
df_lang = df_lang[['Characteristic', 'Total']]
df_lang.columns = ['Language', 'Count']

# --- [CRITICAL FIX] ---
# Strip whitespace from strings. Without this, filters like 'English' vs ' English' fail.
df_lang['Language'] = df_lang['Language'].str.strip()

# Convert Count column to numeric, coercing errors to NaN
df_lang['Count'] = pd.to_numeric(df_lang['Count'], errors='coerce')

# ==========================================
# 3. Define Exclusion List (Manual Feature Engineering)
# ==========================================
# We manually exclude aggregates and broad categories to isolate specific languages.
# This simulates the "Subject Matter Expert" knowledge required for cleaning.
exclusion_list = [
    # Top-level totals
    'Total - Mother tongue for the total population excluding institutional residents - 100% data',
    'Single responses',
    'Multiple responses',
    'English and non-official language(s)',
    
    # Broad official/non-official categories
    'Official languages',
    'Non-official languages',
    'English', 
    'French',
    'Non-Indigenous languages',
    'Indigenous languages',
    
    # Language Families (Aggregates) - Must exclude these to find specific languages
    'Sino-Tibetan languages',
    'Chinese languages',  # Note: This is an aggregate of Mandarin/Cantonese
    'Indo-European languages',
    'Indo-Iranian languages',
    'Italic (Romance) languages',
    'Iranian languages',
    'Persian languages',
    'Indo-Aryan languages',
    'Balto-Slavic languages',
    'Slavic languages',
    'Afro-Asiatic languages',
    'Semitic languages',
    'Germanic languages',
    'Turkic languages',
    'Dravidian languages',
    'Austronesian languages',
    'Tai-Kadai languages'
]

# ==========================================
# 4. Filtering & Sorting
# ==========================================
# Apply the exclusion filter
df_clean = df_lang[~df_lang['Language'].isin(exclusion_list)]

# Sort by count descending and take the top 5
top_5_languages = df_clean.sort_values(by='Count', ascending=False).head(5)

print("\n" + "="*40)
print("TOP 5 NON-OFFICIAL MOTHER TONGUES")
print("(Manual Analysis Result)")
print("="*40)
print(top_5_languages.to_string(index=False))

# ==========================================
# 5. Visualization
# ==========================================
plt.figure(figsize=(12, 7))
bars = plt.bar(top_5_languages['Language'], top_5_languages['Count'], color='#4c72b0', alpha=0.9)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 50, int(yval), ha='center', va='bottom', fontweight='bold')

plt.title('Top 5 Non-Official Mother Tongues (Manual Analysis)', fontsize=15)
plt.xlabel('Language', fontsize=12)
plt.ylabel('Number of Speakers', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()

# Save image instead of showing it (better for servers/headless environments)
plt.savefig(output_image)
print(f"\n[Success] Chart saved to: {output_image}")