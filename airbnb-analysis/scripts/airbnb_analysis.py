#IMPORTING LIBRARIES#
import pandas as pd;
import numpy as np;
import seaborn as sns;
import matplotlib.pyplot as plt
#LOADING DATASET#
data=pd.read_csv('listings.csv');
#PRINT 5 ROWS TO CHECK THE SHAPE AND INFO
print(data.info());
print(data.head(5));
rows,columns = data.shape
print(f'Shape of the dataset ---> Rows: {rows} & Columns: {columns}')
  #checking datatype for each row
pd.set_option('display.max_rows', None)
print(data.dtypes)
    #DATA CLEANING#
#missing values per column
missing_count = data.isnull().sum()
missing_percent = (data.isnull().sum() / len(data)) * 100

missing_table = pd.DataFrame({
    'Missing Count': missing_count,
    'Missing %': missing_percent.round(2)
})

print(missing_table[missing_table['Missing Count'] > 0])
#Drop Entirely (100% missing — useless)

#neighbourhood_group_cleansed
#calendar_updated
#license
#Create Binary Flag → Then Drop (High missing, but existence matters)
#neighborhood_overview (60.88%) → has_neighborhood_overview
#neighbourhood (60.88%) → has_neighbourhood
#host_about (48.12%) → has_host_about
#host_location (26.15%) → has_host_location
#first_review / last_review (14.23%) → has_reviews
#Fill with Median (Numerical)
#host_response_rate, host_acceptance_rate
#bathrooms, beds, price
#estimated_revenue_l365d
#review_scores_* (all 7 score columns)
#reviews_per_month
 #Fill with Mode (Categorical/Boolean)
#host_response_time → mode
#host_is_superhost → False
#has_availability → mode
#Fill with Placeholder (Text)
#description → "No description provided"
#host_neighbourhood → "Unknown"
#Fill with 0 (Night constraints — likely data entry gaps)
#minimum_minimum_nights, maximum_minimum_nights
#minimum_maximum_nights, maximum_maximum_nights
#Fill with Mode (Numeric, low missing)
#bedrooms (1.05%) → mode

# === HANDLE MISSING VALUES ===
# ============================================
# STEP 1: DROP 100% MISSING / USELESS COLUMNS
# ============================================
cols_to_drop = ['neighbourhood_group_cleansed', 'calendar_updated', 'license']
data.drop(columns=[c for c in cols_to_drop if c in data.columns], inplace=True)
# ============================================
# STEP 2: FIX SYMBOL-FORMATTED STRING COLUMNS
# ============================================
# price → "$120.00" to 120.0
data['price'] = data['price'].astype(str).str.replace('$', '', regex=False)\
                                          .str.replace(',', '', regex=False)\
                                          .str.strip()
data['price'] = pd.to_numeric(data['price'], errors='coerce')

# host_response_rate → "95%" to 95.0
data['host_response_rate'] = data['host_response_rate'].astype(str)\
                                                        .str.replace('%', '', regex=False)\
                                                        .str.strip()
data['host_response_rate'] = pd.to_numeric(data['host_response_rate'], errors='coerce')

# host_acceptance_rate → "80%" to 80.0
data['host_acceptance_rate'] = data['host_acceptance_rate'].astype(str)\
                                                            .str.replace('%', '', regex=False)\
                                                            .str.strip()
data['host_acceptance_rate'] = pd.to_numeric(data['host_acceptance_rate'], errors='coerce')

# ============================================
# STEP 3: BINARY FLAGS FOR HIGH MISSING TEXT COLUMNS
# ============================================
flag_map = {
    'has_neighborhood_overview': 'neighborhood_overview',
    'has_neighbourhood':         'neighbourhood',
    'has_host_about':            'host_about',
    'has_host_location':         'host_location',
    'has_reviews':               'first_review',
}
for flag, col in flag_map.items():
    if col in data.columns:
        data[flag] = data[col].notna().astype(int)

# Drop original high-missing text columns
drop_text = ['neighborhood_overview', 'neighbourhood', 'host_about',
             'host_location', 'first_review', 'last_review', 'bathrooms_text']
data.drop(columns=[c for c in drop_text if c in data.columns], inplace=True)

# ============================================
# STEP 4: FILL TEXT / CATEGORICAL COLUMNS
# ============================================
data['description']       = data['description'].fillna('No description provided')
data['host_neighbourhood'] = data['host_neighbourhood'].fillna('Unknown')
data['host_response_time'] = data['host_response_time'].fillna(
                                data['host_response_time'].mode()[0])

# host_is_superhost is 't'/'f' string — fill with 'f'
data['host_is_superhost']  = data['host_is_superhost'].fillna('f')

# has_availability is 't'/'f' string — fill with mode
data['has_availability']   = data['has_availability'].fillna(
                                data['has_availability'].mode()[0])

# instant_bookable is 't'/'f' string — fill with mode
data['instant_bookable']   = data['instant_bookable'].fillna(
                                data['instant_bookable'].mode()[0])

# ============================================
# STEP 5: FILL NUMERIC COLUMNS WITH MEDIAN
# ============================================
median_cols = [
    'price', 'host_response_rate', 'host_acceptance_rate',
    'bathrooms', 'beds', 'estimated_revenue_l365d', 'reviews_per_month',
    'review_scores_rating', 'review_scores_accuracy',
    'review_scores_cleanliness', 'review_scores_checkin',
    'review_scores_communication', 'review_scores_location',
    'review_scores_value'
]
for col in median_cols:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        data[col] = data[col].fillna(data[col].median())

# ============================================
# STEP 6: FILL BEDROOMS WITH MODE
# ============================================
data['bedrooms'] = pd.to_numeric(data['bedrooms'], errors='coerce')
data['bedrooms'] = data['bedrooms'].fillna(data['bedrooms'].mode()[0])

# ============================================
# STEP 7: FILL NIGHT COLUMNS WITH MEDIAN
# ============================================
night_cols = [
    'minimum_minimum_nights', 'maximum_minimum_nights',
    'minimum_maximum_nights', 'maximum_maximum_nights'
]
for col in night_cols:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        data[col] = data[col].fillna(data[col].median())

# ============================================
# STEP 8: FINAL VERIFICATION
# ============================================
remaining = data.isnull().sum()
remaining = remaining[remaining > 0]
if remaining.empty:
    print("✅ All missing values handled!")
else:
    print("⚠️ Still missing:\n", remaining)

print("\nShape:", data.shape)
print("\nDtypes:\n", data.dtypes.to_string())
#======Removing Duplicates====
# ============================================
# DUPLICATE CHECK
# ============================================

# 1. Total duplicate rows
print("Total duplicate rows:", data.duplicated().sum())

# 2. View the duplicate rows
duplicates = data[data.duplicated(keep=False)]
print("\nDuplicate rows:\n", duplicates)

# 3. Remove duplicates
data = data.drop_duplicates()
print("\n✅ Duplicates removed!")
print("Shape after removing duplicates:", data.shape)
#Exploratory Data analysis
#summary of statistical columns
# 2. Full summary - all numeric columns clearly
# Print each column's stats one by one — guaranteed full output
summary = data.describe().T
for col in summary.index:
    print(f"\n📊 {col}")
    print(f"   count: {summary.loc[col,'count']:.0f}  |  mean: {summary.loc[col,'mean']:.2f}  |  std: {summary.loc[col,'std']:.2f}")
    print(f"   min: {summary.loc[col,'min']:.2f}  |  25%: {summary.loc[col,'25%']:.2f}  |  50%: {summary.loc[col,'50%']:.2f}  |  75%: {summary.loc[col,'75%']:.2f}  |  max: {summary.loc[col,'max']:.2f}")
# ============================================
# DISTRIBUTION OF KEY VARIABLES
# ============================================
fig, axes = plt.subplots(3, 3, figsize=(18, 15))
fig.suptitle('Distribution of Key Variables', fontsize=16, fontweight='bold')
# Price - Raw
sns.histplot(data['price'], bins=50, kde=True, ax=axes[0,0], color='steelblue')
axes[0,0].set_title('Price Distribution (Raw)')
axes[0,0].set_xlabel('Price ($)')

# Price - Log transformed (better view, removes skew)
sns.histplot(data['price'][data['price'] > 0], bins=50, kde=True, 
             ax=axes[0,1], color='steelblue', log_scale=True)
axes[0,1].set_title('Price Distribution (Log Scale)')
axes[0,1].set_xlabel('Price ($) - Log Scale')
# Price - Boxplot (shows outliers)
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# DISTRIBUTION OF KEY VARIABLES
# ============================================

fig, axes = plt.subplots(3, 3, figsize=(18, 15))
fig.suptitle('Distribution of Key Variables', fontsize=16, fontweight='bold')

# ============================================
# 1. PRICE DISTRIBUTION
# ============================================

# Price - Raw
sns.histplot(data['price'], bins=50, kde=True, ax=axes[0,0], color='steelblue')
axes[0,0].set_title('Price Distribution (Raw)')
axes[0,0].set_xlabel('Price ($)')

# Price - Log transformed (better view, removes skew)
sns.histplot(data['price'][data['price'] > 0], bins=50, kde=True, 
             ax=axes[0,1], color='steelblue', log_scale=True)
axes[0,1].set_title('Price Distribution (Log Scale)')
axes[0,1].set_xlabel('Price ($) - Log Scale')

# Price - Boxplot (shows outliers)
sns.boxplot(y=data['price'], ax=axes[0,2], color='steelblue')
axes[0,2].set_title('Price Boxplot (Outliers)')
axes[0,2].set_ylabel('Price ($)')

# ============================================
# 2. REVIEWS DISTRIBUTION
# ============================================

# Number of reviews
sns.histplot(data['number_of_reviews'], bins=50, kde=True, 
             ax=axes[1,0], color='coral')
axes[1,0].set_title('Number of Reviews Distribution')
axes[1,0].set_xlabel('Number of Reviews')

# Review scores rating
sns.histplot(data['review_scores_rating'], bins=30, kde=True, 
             ax=axes[1,1], color='coral')
axes[1,1].set_title('Review Scores Rating Distribution')
axes[1,1].set_xlabel('Rating Score')

# Reviews per month
sns.histplot(data['reviews_per_month'], bins=50, kde=True, 
             ax=axes[1,2], color='coral')
axes[1,2].set_title('Reviews Per Month Distribution')
axes[1,2].set_xlabel('Reviews Per Month')

# ============================================
# 3. LOCATION DISTRIBUTION
# ============================================

# Top 10 neighbourhoods by listing count
top_neighbourhoods = data['host_neighbourhood'].value_counts().head(10)
sns.barplot(x=top_neighbourhoods.values, y=top_neighbourhoods.index, 
            ax=axes[2,0], color='green')
axes[2,0].set_title('Top 10 Neighbourhoods')
axes[2,0].set_xlabel('Number of Listings')

# Review scores by location score distribution
sns.histplot(data['review_scores_location'], bins=30, kde=True, 
             ax=axes[2,1], color='green')
axes[2,1].set_title('Location Score Distribution')
axes[2,1].set_xlabel('Location Score')

# Availability 365 distribution
sns.histplot(data['availability_365'], bins=50, kde=True, 
             ax=axes[2,2], color='green')
axes[2,2].set_title('Availability (365 days)')
axes[2,2].set_xlabel('Days Available')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/distribution_plots.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Saved to distribution_plots.png")
# ============================================
# 1. FIX PRICE SKEWNESS — LOG TRANSFORM
# ============================================
print("=== PRICE ===")
print(f"Skewness Before: {data['price'].skew():.2f}")

data['price_log'] = np.log1p(data['price'])

print(f"Skewness After:  {data['price_log'].skew():.2f}")

# ============================================
# 2. FIX NUMBER OF REVIEWS — LOG TRANSFORM
# ============================================
print("\n=== NUMBER OF REVIEWS ===")
print(f"Skewness Before: {data['number_of_reviews'].skew():.2f}")

data['reviews_log'] = np.log1p(data['number_of_reviews'])

print(f"Skewness After:  {data['reviews_log'].skew():.2f}")

# ============================================
# 3. PLOT BEFORE vs AFTER FOR BOTH
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Skewness Fix — Before vs After', fontsize=14, fontweight='bold')

# Price Before
sns.histplot(data['price'], bins=50, kde=True, ax=axes[0,0], color='salmon')
axes[0,0].set_title(f'Price - Before\nSkew: {data["price"].skew():.2f}')
axes[0,0].set_xlabel('Price ($)')

# Price After
sns.histplot(data['price_log'], bins=50, kde=True, ax=axes[0,1], color='seagreen')
axes[0,1].set_title(f'Price - After Log\nSkew: {data["price_log"].skew():.2f}')
axes[0,1].set_xlabel('Log(Price)')

# Reviews Before
sns.histplot(data['number_of_reviews'], bins=50, kde=True, ax=axes[1,0], color='salmon')
axes[1,0].set_title(f'Reviews - Before\nSkew: {data["number_of_reviews"].skew():.2f}')
axes[1,0].set_xlabel('Number of Reviews')

# Reviews After
sns.histplot(data['reviews_log'], bins=50, kde=True, ax=axes[1,1], color='seagreen')
axes[1,1].set_title(f'Reviews - After Log\nSkew: {data["reviews_log"].skew():.2f}')
axes[1,1].set_xlabel('Log(Number of Reviews)')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/skewness_fixed.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n✅ Skewness fix complete!")

#count number properties per neighbourhood,roomtypeetc]
# ============================================
# 1. PROPERTIES PER NEIGHBOURHOOD
# ============================================
neighbourhood_counts = data['host_neighbourhood'].value_counts().head(15)
print("=== TOP 15 NEIGHBOURHOODS ===")
print(neighbourhood_counts.to_string())

# ============================================
# 2. PROPERTIES PER ROOM TYPE
# ============================================
room_type_counts = data['room_type'].value_counts()
print("\n=== ROOM TYPE COUNTS ===")
print(room_type_counts.to_string())

# ============================================
# 3. PROPERTIES PER HOST (TOP 10)
# ============================================
host_counts = data['host_name'].value_counts().head(10)
print("\n=== TOP 10 HOSTS BY LISTINGS ===")
print(host_counts.to_string())

# ============================================
# 4. PROPERTIES BY INSTANT BOOKABLE
# ============================================
instant_counts = data['instant_bookable'].value_counts()
print("\n=== INSTANT BOOKABLE ===")
print(instant_counts.to_string())

# ============================================
# 5. PROPERTIES BY SUPERHOST STATUS
# ============================================
superhost_counts = data['host_is_superhost'].value_counts()
print("\n=== SUPERHOST STATUS ===")
print(superhost_counts.to_string())

# ============================================
# 6. PROPERTIES BY HOST RESPONSE TIME
# ============================================
response_time_counts = data['host_response_time'].value_counts()
print("\n=== HOST RESPONSE TIME ===")
print(response_time_counts.to_string())

# ============================================
# PLOTS
# ============================================
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Property Count Analysis', fontsize=16, fontweight='bold')

# Plot 1 - Neighbourhood
sns.barplot(x=neighbourhood_counts.values,
            y=neighbourhood_counts.index,
            ax=axes[0,0], color='steelblue')
axes[0,0].set_title('Top 15 Neighbourhoods')
axes[0,0].set_xlabel('Number of Properties')

# Plot 2 - Room Type Bar
sns.barplot(x=room_type_counts.values,
            y=room_type_counts.index,
            ax=axes[0,1], color='coral')
axes[0,1].set_title('Properties by Room Type')
axes[0,1].set_xlabel('Number of Properties')

# Plot 3 - Room Type Pie
axes[0,2].pie(room_type_counts.values,
              labels=room_type_counts.index,
              autopct='%1.1f%%',
              colors=['steelblue','coral','seagreen','orange'])
axes[0,2].set_title('Room Type Distribution (%)')

# Plot 4 - Top 10 Hosts
sns.barplot(x=host_counts.values,
            y=host_counts.index,
            ax=axes[1,0], color='purple')
axes[1,0].set_title('Top 10 Hosts by Listings')
axes[1,0].set_xlabel('Number of Listings')

# Plot 5 - Superhost Pie
axes[1,1].pie(superhost_counts.values,
              labels=['Superhost' if x == 't' else 'Not Superhost'
                      for x in superhost_counts.index],
              autopct='%1.1f%%',
              colors=['gold','lightgrey'])
axes[1,1].set_title('Superhost Status (%)')

# Plot 6 - Host Response Time
sns.barplot(x=response_time_counts.values,
            y=response_time_counts.index,
            ax=axes[1,2], color='seagreen')
axes[1,2].set_title('Host Response Time')
axes[1,2].set_xlabel('Number of Properties')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/property_counts.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Property count analysis saved!")
#====IDENTIFY THE CORELATION BETWEEN VARIABLE===#
#Numerical vs Numerical → Correlation Matrix (Heatmap)


# Select only numeric columns
numeric_cols = data.select_dtypes(include='number').corr(method='spearman')

plt.figure(figsize=(18, 14))
sns.heatmap(numeric_cols, 
            annot=True,       # show values
            fmt='.2f',        # 2 decimal places
            cmap='coolwarm',  # red=positive, blue=negative
            center=0,
            linewidths=0.5)
plt.title('Correlation Matrix - Numerical Variables', fontsize=16)
plt.tight_layout()
plt.savefig('C:/Airbnb assignment/correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Correlation matrix saved!")
#since columns are crowded i chose only 15 columns for correlation matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================
# SELECT ONLY KEY COLUMNS FOR CORRELATION
# ============================================
key_cols = [
    'price',
    'accommodates',
    'bathrooms',
    'bedrooms',
    'beds',
    'minimum_nights',
    'availability_365',
    'number_of_reviews',
    'reviews_per_month',
    'review_scores_rating',
    'review_scores_location',
    'review_scores_cleanliness',
    'host_response_rate',
    'host_acceptance_rate',
    'estimated_revenue_l365d'
]

# Filter only columns that exist in data
key_cols = [col for col in key_cols if col in data.columns]

# Compute correlation
corr_matrix = data[key_cols].corr(method='spearman')

# ============================================
# PLOT CLEAN HEATMAP
# ============================================
plt.figure(figsize=(14, 10))
sns.heatmap(corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            linewidths=0.8,
            annot_kws={'size': 9})

plt.title('Correlation Matrix - Key Variables', fontsize=16, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('C:/Airbnb assignment/correlation_clean.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Clean correlation matrix saved!")

# ============================================
# PRINT TOP CORRELATIONS WITH PRICE
# ============================================
price_corr = corr_matrix['price'].drop('price').sort_values(ascending=False)
print("\n=== CORRELATION WITH PRICE (High to Low) ===")
print(price_corr.to_string())
#Categorical vs Numerical → Boxplot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Categorical vs Price', fontsize=14, fontweight='bold')

# Room type vs Price
sns.boxplot(x='room_type', y='price', data=data, ax=axes[0], palette='Set2')
axes[0].set_title('Room Type vs Price')
axes[0].tick_params(axis='x', rotation=15)

# Superhost vs Price
sns.boxplot(x='host_is_superhost', y='price', data=data, ax=axes[1], palette='Set2')
axes[1].set_title('Superhost vs Price')
axes[1].set_xticklabels(['Not Superhost', 'Superhost'])

# Instant Bookable vs Price
sns.boxplot(x='instant_bookable', y='price', data=data, ax=axes[2], palette='Set2')
axes[2].set_title('Instant Bookable vs Price')
axes[2].set_xticklabels(['Not Instant', 'Instant'])

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/categorical_vs_price.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Categorical vs Price saved!")
##Numerical vs Numerical → Scatter Plot (Key Variables)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Scatter Plots - Key Relationships', fontsize=14, fontweight='bold')

# Price vs Reviews
axes[0].scatter(data['number_of_reviews'], data['price'], alpha=0.3, color='steelblue')
axes[0].set_xlabel('Number of Reviews')
axes[0].set_ylabel('Price')
axes[0].set_title('Price vs Number of Reviews')

# Price vs Rating
axes[1].scatter(data['review_scores_rating'], data['price'], alpha=0.3, color='coral')
axes[1].set_xlabel('Review Score Rating')
axes[1].set_ylabel('Price')
axes[1].set_title('Price vs Review Rating')

# Price vs Availability
axes[2].scatter(data['availability_365'], data['price'], alpha=0.3, color='seagreen')
axes[2].set_xlabel('Availability (365 days)')
axes[2].set_ylabel('Price')
axes[2].set_title('Price vs Availability')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/scatter_plots.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Scatter plots saved!")
#pricing analysis#
#what are the price ranges for different neighbourhood or room types

# ============================================
# 1. PRICE RANGE BY ROOM TYPE
# ============================================
print("=== PRICE RANGE BY ROOM TYPE ===")
print(data.groupby('room_type')['price'].agg(['min','max','mean','median']).round(2).to_string())

# ============================================
# 2. PRICE RANGE BY TOP 10 NEIGHBOURHOODS
# ============================================
top10_neighbourhoods = data['host_neighbourhood'].value_counts().head(10).index
neighbourhood_price = data[data['host_neighbourhood'].isin(top10_neighbourhoods)]\
                      .groupby('host_neighbourhood')['price']\
                      .agg(['min','max','mean','median']).round(2)

print("\n=== PRICE RANGE BY TOP 10 NEIGHBOURHOODS ===")
print(neighbourhood_price.to_string())

# ============================================
# PLOTS
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Price Ranges by Neighbourhood & Room Type', 
             fontsize=16, fontweight='bold')

# Plot 1 - Boxplot: Price by Room Type
sns.boxplot(x='room_type', y='price', data=data, 
            palette='Set2', ax=axes[0,0])
axes[0,0].set_title('Price Distribution by Room Type')
axes[0,0].set_xlabel('Room Type')
axes[0,0].set_ylabel('Price ($)')
axes[0,0].tick_params(axis='x', rotation=15)

# Plot 2 - Boxplot: Price by Top 10 Neighbourhoods
top10_data = data[data['host_neighbourhood'].isin(top10_neighbourhoods)]
sns.boxplot(y='host_neighbourhood', x='price', 
            data=top10_data, palette='Set3', ax=axes[0,1])
axes[0,1].set_title('Price Distribution by Top 10 Neighbourhoods')
axes[0,1].set_xlabel('Price ($)')
axes[0,1].set_ylabel('Neighbourhood')

# Plot 3 - Mean Price by Room Type Bar
room_mean = data.groupby('room_type')['price'].mean().sort_values(ascending=False)
sns.barplot(x=room_mean.index, y=room_mean.values, 
            palette='Set2', ax=axes[1,0])
axes[1,0].set_title('Average Price by Room Type')
axes[1,0].set_xlabel('Room Type')
axes[1,0].set_ylabel('Average Price ($)')
axes[1,0].tick_params(axis='x', rotation=15)
# Add value labels on bars
for i, v in enumerate(room_mean.values):
    axes[1,0].text(i, v + 1, f'${v:.0f}', ha='center', fontweight='bold')

# Plot 4 - Mean Price by Top 10 Neighbourhoods Bar
neighbourhood_mean = top10_data.groupby('host_neighbourhood')['price']\
                    .mean().sort_values(ascending=False)
sns.barplot(x=neighbourhood_mean.values, y=neighbourhood_mean.index,
            palette='Set3', ax=axes[1,1])
axes[1,1].set_title('Average Price by Top 10 Neighbourhoods')
axes[1,1].set_xlabel('Average Price ($)')
axes[1,1].set_ylabel('Neighbourhood')
# Add value labels on bars
for i, v in enumerate(neighbourhood_mean.values):
    axes[1,1].text(v + 0.5, i, f'${v:.0f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/price_ranges.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Price range analysis saved!")
#How does the number of reviews impact the price
##what are the top rated neighbourhoods
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# TOP RATED NEIGHBOURHOODS
# ============================================

# Average rating per neighbourhood (min 5 listings for reliability)
neighbourhood_ratings = data.groupby('host_neighbourhood').agg(
    avg_rating    = ('review_scores_rating', 'mean'),
    avg_price     = ('price', 'mean'),
    total_listings= ('price', 'count'),
    avg_location  = ('review_scores_location', 'mean'),
    avg_cleanliness=('review_scores_cleanliness', 'mean')
).round(2)

# Filter neighbourhoods with at least 5 listings
neighbourhood_ratings = neighbourhood_ratings[
    neighbourhood_ratings['total_listings'] >= 5
].sort_values('avg_rating', ascending=False)

print("=== TOP 10 RATED NEIGHBOURHOODS ===")
print(neighbourhood_ratings.head(10).to_string())

print("\n=== BOTTOM 5 RATED NEIGHBOURHOODS ===")
print(neighbourhood_ratings.tail(5).to_string())

# ============================================
# PLOTS
# ============================================
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.suptitle('Top Rated Neighbourhoods Analysis', fontsize=16, fontweight='bold')

# Plot 1 - Top 10 by Rating
top10 = neighbourhood_ratings.head(10)
sns.barplot(x='avg_rating', y=top10.index, 
            data=top10, palette='RdYlGn', ax=axes[0])
axes[0].set_title('Top 10 Neighbourhoods by Rating')
axes[0].set_xlabel('Average Rating')
axes[0].set_xlim(4.0, 5.0)
for i, v in enumerate(top10['avg_rating']):
    axes[0].text(v + 0.01, i, f'{v:.2f}', va='center', fontweight='bold')

# Plot 2 - Rating vs Price bubble chart
scatter = axes[1].scatter(
    neighbourhood_ratings['avg_price'],
    neighbourhood_ratings['avg_rating'],
    s=neighbourhood_ratings['total_listings'] * 10,
    alpha=0.6,
    c=neighbourhood_ratings['avg_rating'],
    cmap='RdYlGn'
)
axes[1].set_title('Rating vs Price\n(bubble size = number of listings)')
axes[1].set_xlabel('Average Price ($)')
axes[1].set_ylabel('Average Rating')
plt.colorbar(scatter, ax=axes[1])

# Annotate top 5
for idx, row in neighbourhood_ratings.head(5).iterrows():
    axes[1].annotate(idx, 
                     (row['avg_price'], row['avg_rating']),
                     fontsize=7, ha='center')

# Plot 3 - Top 10 by Location Score
top10_location = neighbourhood_ratings.sort_values(
    'avg_location', ascending=False).head(10)
sns.barplot(x='avg_location', y=top10_location.index,
            data=top10_location, palette='Blues_r', ax=axes[2])
axes[2].set_title('Top 10 Neighbourhoods by Location Score')
axes[2].set_xlabel('Average Location Score')
axes[2].set_xlim(4.0, 5.0)
for i, v in enumerate(top10_location['avg_location']):
    axes[2].text(v + 0.01, i, f'{v:.2f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/top_rated_neighbourhoods.png', 
            dpi=150, bbox_inches='tight')
plt.show()
print("✅ Top rated neighbourhoods analysis saved!")
#which neighbourhoods have the highest number of listings

# ============================================
# NEIGHBOURHOODS WITH HIGHEST LISTINGS
# ============================================

# Count listings per neighbourhood
neighbourhood_listings = data['host_neighbourhood'].value_counts()

print("=== ALL NEIGHBOURHOODS BY LISTING COUNT ===")
print(neighbourhood_listings.to_string())

print(f"\nTotal Neighbourhoods: {len(neighbourhood_listings)}")
print(f"Top Neighbourhood   : {neighbourhood_listings.index[0]} ({neighbourhood_listings.iloc[0]} listings)")

# ============================================
# PLOTS
# ============================================
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Neighbourhoods by Number of Listings', fontsize=16, fontweight='bold')

# Plot 1 - Top 15 Neighbourhoods
top15 = neighbourhood_listings.head(15)
sns.barplot(x=top15.values, y=top15.index, palette='Blues_r', ax=axes[0])
axes[0].set_title('Top 15 Neighbourhoods by Listings')
axes[0].set_xlabel('Number of Listings')
axes[0].set_ylabel('Neighbourhood')
for i, v in enumerate(top15.values):
    axes[0].text(v + 0.3, i, str(v), va='center', fontweight='bold')

# Plot 2 - Pie chart Top 10
top10 = neighbourhood_listings.head(10)
others = neighbourhood_listings.iloc[10:].sum()
pie_values = list(top10.values) + [others]
pie_labels = list(top10.index) + ['Others']
axes[1].pie(pie_values, labels=pie_labels,
            autopct='%1.1f%%',
            colors=sns.color_palette('Blues_r', len(pie_values)))
axes[1].set_title('Top 10 Neighbourhoods Share of Total Listings (%)')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/listings_per_neighbourhood.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("✅ Listings per neighbourhood saved!")
#sentiment analysis
# ============================================
# SENTIMENT BASED ON REVIEW SCORES
# ============================================

# Classify sentiment based on review_scores_rating
def classify_sentiment(score):
    if score >= 4.5:
        return 'Positive'
    elif score >= 3.5:
        return 'Neutral'
    else:
        return 'Negative'

data['sentiment'] = data['review_scores_rating'].apply(classify_sentiment)

# ============================================
# COUNTS & PERCENTAGES
# ============================================
sentiment_counts = data['sentiment'].value_counts()
sentiment_pct    = (data['sentiment'].value_counts(normalize=True) * 100).round(2)

print("=== SENTIMENT COUNTS ===")
print(sentiment_counts.to_string())
print("\n=== SENTIMENT PERCENTAGE ===")
print(sentiment_pct.to_string())

# ============================================
# SENTIMENT BY ROOM TYPE
# ============================================
print("\n=== SENTIMENT BY ROOM TYPE ===")
room_sentiment = pd.crosstab(data['room_type'],
                              data['sentiment'],
                              normalize='index') * 100
print(room_sentiment.round(2).to_string())

# ============================================
# SENTIMENT BY NEIGHBOURHOOD (TOP 10)
# ============================================
print("\n=== SENTIMENT BY TOP 10 NEIGHBOURHOODS ===")
top10 = data['host_neighbourhood'].value_counts().head(10).index
neigh_sentiment = data[data['host_neighbourhood'].isin(top10)]\
                  .groupby('host_neighbourhood')['review_scores_rating']\
                  .agg(['mean','count']).round(2)\
                  .sort_values('mean', ascending=False)
print(neigh_sentiment.to_string())

# ============================================
# PLOTS
# ============================================
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('Review Sentiment Analysis', fontsize=16, fontweight='bold')

colors = {'Positive': 'seagreen', 'Neutral': 'steelblue', 'Negative': 'salmon'}

# Plot 1 - Sentiment Bar
sns.barplot(x=sentiment_counts.index,
            y=sentiment_counts.values,
            palette=[colors[s] for s in sentiment_counts.index],
            ax=axes[0,0])
axes[0,0].set_title('Sentiment Distribution')
axes[0,0].set_xlabel('Sentiment')
axes[0,0].set_ylabel('Count')
for i, v in enumerate(sentiment_counts.values):
    axes[0,0].text(i, v + 1, str(v), ha='center', fontweight='bold')

# Plot 2 - Sentiment Pie
axes[0,1].pie(sentiment_counts.values,
              labels=sentiment_counts.index,
              autopct='%1.1f%%',
              colors=[colors[s] for s in sentiment_counts.index])
axes[0,1].set_title('Sentiment Share (%)')

# Plot 3 - Rating Distribution
sns.histplot(data['review_scores_rating'].dropna(),
             bins=30, kde=True, ax=axes[0,2], color='steelblue')
axes[0,2].axvline(x=4.5, color='green', linestyle='--', label='Positive (>=4.5)')
axes[0,2].axvline(x=3.5, color='orange', linestyle='--', label='Neutral (3.5-4.5)')
axes[0,2].set_title('Rating Score Distribution')
axes[0,2].set_xlabel('Review Score Rating')
axes[0,2].legend()

# Plot 4 - Sentiment by Room Type
room_sentiment_plot = data.groupby(['room_type', 'sentiment'])\
                          .size().unstack(fill_value=0)
room_sentiment_plot.plot(kind='bar', ax=axes[1,0],
                         color=[colors[s] for s in room_sentiment_plot.columns])
axes[1,0].set_title('Sentiment by Room Type')
axes[1,0].set_xlabel('Room Type')
axes[1,0].set_ylabel('Count')
axes[1,0].tick_params(axis='x', rotation=15)
axes[1,0].legend(title='Sentiment')

# Plot 5 - Price by Sentiment Boxplot
sns.boxplot(x='sentiment', y='price', data=data,
            palette=colors, ax=axes[1,1])
axes[1,1].set_title('Price by Sentiment')
axes[1,1].set_xlabel('Sentiment')
axes[1,1].set_ylabel('Price ($)')

# Plot 6 - Avg Rating by Top 10 Neighbourhoods
sns.barplot(x='mean', y=neigh_sentiment.index,
            data=neigh_sentiment.reset_index(),
            palette='RdYlGn', ax=axes[1,2])
axes[1,2].set_title('Avg Rating by Top 10 Neighbourhoods')
axes[1,2].set_xlabel('Average Rating')
axes[1,2].set_xlim(4.0, 5.0)
for i, v in enumerate(neigh_sentiment['mean']):
    axes[1,2].text(v + 0.01, i, f'{v:.2f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/sentiment_analysis.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("✅ Sentiment analysis saved!")
#review distribution by neighbourhood or room type

# ============================================
# 1. REVIEW DISTRIBUTION BY NEIGHBOURHOOD
# ============================================
top10 = data['host_neighbourhood'].value_counts().head(10).index
neigh_data = data[data['host_neighbourhood'].isin(top10)]

# ============================================
# 2. REVIEW DISTRIBUTION BY ROOM TYPE
# ============================================
fig, axes = plt.subplots(3, 2, figsize=(18, 18))
fig.suptitle('Review Distribution by Neighbourhood & Room Type',
             fontsize=16, fontweight='bold')

# Plot 1 - Avg Rating by Neighbourhood Bar
neigh_rating = neigh_data.groupby('host_neighbourhood')\
               ['review_scores_rating'].mean()\
               .sort_values(ascending=False)
sns.barplot(x=neigh_rating.values,
            y=neigh_rating.index,
            palette='RdYlGn', ax=axes[0,0])
axes[0,0].set_title('Avg Review Rating by Top 10 Neighbourhoods')
axes[0,0].set_xlabel('Average Rating')
axes[0,0].set_xlim(4.0, 5.0)
for i, v in enumerate(neigh_rating.values):
    axes[0,0].text(v + 0.01, i, f'{v:.2f}',
                   va='center', fontweight='bold')

# Plot 2 - Avg Rating by Room Type Bar
room_rating = data.groupby('room_type')\
              ['review_scores_rating'].mean()\
              .sort_values(ascending=False)
sns.barplot(x=room_rating.index,
            y=room_rating.values,
            palette='Set2', ax=axes[0,1])
axes[0,1].set_title('Avg Review Rating by Room Type')
axes[0,1].set_xlabel('Room Type')
axes[0,1].set_ylabel('Average Rating')
axes[0,1].set_ylim(4.0, 5.0)
axes[0,1].tick_params(axis='x', rotation=15)
for i, v in enumerate(room_rating.values):
    axes[0,1].text(i, v + 0.005, f'{v:.2f}',
                   ha='center', fontweight='bold')

# Plot 3 - Boxplot Rating by Neighbourhood
sns.boxplot(y='host_neighbourhood', x='review_scores_rating',
            data=neigh_data, palette='RdYlGn', ax=axes[1,0])
axes[1,0].set_title('Rating Distribution by Neighbourhood')
axes[1,0].set_xlabel('Review Score Rating')
axes[1,0].set_ylabel('Neighbourhood')
axes[1,0].axvline(x=4.5, color='green',
                  linestyle='--', label='Positive threshold')
axes[1,0].legend()

# Plot 4 - Boxplot Rating by Room Type
sns.boxplot(x='room_type', y='review_scores_rating',
            data=data, palette='Set2', ax=axes[1,1])
axes[1,1].set_title('Rating Distribution by Room Type')
axes[1,1].set_xlabel('Room Type')
axes[1,1].set_ylabel('Review Score Rating')
axes[1,1].tick_params(axis='x', rotation=15)
axes[1,1].axhline(y=4.5, color='green',
                  linestyle='--', label='Positive threshold')
axes[1,1].legend()

# Plot 5 - Sentiment Count by Neighbourhood Stacked Bar
neigh_sentiment = neigh_data.groupby(
    ['host_neighbourhood', 'sentiment']).size().unstack(fill_value=0)
neigh_sentiment.plot(kind='barh', stacked=True,
                     color=['salmon', 'steelblue', 'seagreen'],
                     ax=axes[2,0])
axes[2,0].set_title('Sentiment Count by Neighbourhood')
axes[2,0].set_xlabel('Number of Listings')
axes[2,0].set_ylabel('Neighbourhood')
axes[2,0].legend(title='Sentiment')

# Plot 6 - Sentiment Count by Room Type Stacked Bar
room_sentiment = data.groupby(
    ['room_type', 'sentiment']).size().unstack(fill_value=0)
room_sentiment.plot(kind='bar', stacked=True,
                    color=['salmon', 'steelblue', 'seagreen'],
                    ax=axes[2,1])
axes[2,1].set_title('Sentiment Count by Room Type')
axes[2,1].set_xlabel('Room Type')
axes[2,1].set_ylabel('Number of Listings')
axes[2,1].tick_params(axis='x', rotation=15)
axes[2,1].legend(title='Sentiment')

plt.tight_layout()
plt.savefig('C:/Airbnb assignment/review_distribution.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("✅ Review distribution saved!")

# ============================================
# PRINT SUMMARY TABLES
# ============================================
print("\n=== AVG RATING BY NEIGHBOURHOOD ===")
print(neigh_data.groupby('host_neighbourhood')
      ['review_scores_rating']
      .agg(['mean','count','min','max'])
      .round(2).sort_values('mean', ascending=False)
      .to_string())

print("\n=== AVG RATING BY ROOM TYPE ===")
print(data.groupby('room_type')
      ['review_scores_rating']
      .agg(['mean','count','min','max'])
      .round(2).sort_values('mean', ascending=False)
      .to_string())
           ###exporting cleaned data##
data.to_csv('C:/Airbnb assignment/cleaned_airbnb.csv', 
index=False)
print("✅ Cleaned data exported!")
print(f"Total rows    : {len(data)}")
print(f"Total columns : {len(data.columns)}")
print(f"Saved at      : C:/Airbnb assignment/cleaned_airbnb.csv")
 
