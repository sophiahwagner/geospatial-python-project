import requests
import geopandas as gpd
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Pull Virginia diabetes data for 2021
va_diabetes = "https://data.cdc.gov/resource/em5e-5hvn.json?stateabbr=VA&measureid=DIABETES&$limit=5000"
response = requests.get(va_diabetes)
va_diabetes_data = response.json()

# Isolate data into a data frame and identify core attributes
df = pd.DataFrame(va_diabetes_data)
print(df.head())
print(df.info())
print(list(df.columns))
print(df['data_value'])

from shapely.geometry import Point

# Isolate the latitude and longitude values from the geolocation column into two separate columns
df['longitude'] = df['geolocation'].apply(lambda x: float(x['coordinates'][0]) if isinstance(x, dict) and 'coordinates' in x else None)
df['latitude'] = df['geolocation'].apply(lambda x: float(x['coordinates'][1]) if isinstance(x, dict) and 'coordinates' in x else None)
print(df['latitude'],df['longitude'])

# Convert data_value column to numeric
df['data_value'] = pd.to_numeric(df['data_value'])
print(df['data_value'].dtype)

# Create a geo data frame
gdf = gpd.GeoDataFrame(
    df,
    geometry = gpd.points_from_xy(df['longitude'],df['latitude']),
    crs = 'EPSG:4326'
)
print(gdf[['locationname', 'measure','data_value','geometry']].head())

# Create a plot for diabetes prevalence in virginia in 2021
fig, ax = plt.subplots(figsize = (8, 10))
gdf.plot(ax = ax, column = 'data_value', cmap = 'OrRd', legend = True, legend_kwds = {'label': 'Diabetes Prevalence (%)'}, markersize = 15)
ax.set_title("Diabetes Prevalence by Census Tract - Virginia, 2021")
ax.set_axis_off()
# plt.show()

## Pull Virginia obesity data for 2021
va_obesity = 'https://data.cdc.gov/resource/em5e-5hvn.json?stateabbr=VA&measureid=OBESITY&$limit=5000'
response2 = requests.get(va_obesity)
va_obesity_data = response2.json()

## Isolate data into a data frame and identify core attributes
df2 = pd.DataFrame(va_obesity_data)
print(df2.head())
print(list(df2.columns))
print(df2['data_value'])

# Isolate the latitude and longitude values from the geolocation column into two separate columns
df2['longitude'] = df['geolocation'].apply(
    lambda x: float(x['coordinates'][0]) if isinstance(x, dict) and 'coordinates' in x else None
)
df2['latitude'] = df['geolocation'].apply(
    lambda x: float(x['coordinates'][1]) if isinstance(x, dict) and 'coordinates' in x else None
)

# Convert data_value column to numeric
df2['data_value'] = pd.to_numeric(df2['data_value'])

# Create a geo data frame
gdf2 = gpd.GeoDataFrame(
    data = df2, 
    geometry = gpd.points_from_xy(df2['longitude'], df2['latitude']), 
    crs = 'EPSG:4326')

# Create a plot for obesity prevalence in Virginia in 2021
print(gdf[['locationname', 'measure','data_value','geometry']].head())
fig, ax = plt.subplots(figsize = (8, 10))
gdf2.plot(ax = ax, column = 'data_value', cmap = 'OrRd', legend = True, legend_kwds = {'label': 'Obesity Prevalence (%)'}, markersize = 15)
ax.set_title("Obesity Prevalence by Census Tract - Virginia, 2021")
ax.set_axis_off()
##plt.show()

# Shrink both data frames down to include only essential, distinct columns and rename data_value columns for clarity in merged dataset
diabetes_df = df[['locationid', 'geolocation', 'data_value']].rename(columns={'data_value': 'diabetes_value'})
obesity_df  = df2[['locationid', 'data_value']].rename(columns={'data_value': 'obesity_value'})

# Merge the datasets
merged_df = pd.merge(diabetes_df, obesity_df, on = 'locationid')
print(list(merged_df.columns))

#Isolate the latitude and longitude values from the geolocation column into two separate columns
merged_df['longitude'] = merged_df['geolocation'].apply(
    lambda x: float(x['coordinates'][0]) if isinstance(x, dict) and 'coordinates' in x else None
)
merged_df['latitude'] = merged_df['geolocation'].apply(
    lambda x: float(x['coordinates'][1]) if isinstance(x, dict) and 'coordinates' in x else None
)

# Create a geo data frame
gdf_merged = gpd.GeoDataFrame(
    data = merged_df,
    geometry = gpd.points_from_xy(merged_df['longitude'], merged_df['latitude']),
    crs = 'EPSG:4326')

# Check correlation between diabetes and obesity 
correlation = merged_df['diabetes_value'].corr(merged_df['obesity_value'])
print(correlation)

# Pull Maryland diabetes data
md_diabetes = "https://data.cdc.gov/resource/em5e-5hvn.json?stateabbr=MD&measureid=DIABETES&$limit=5000"
response3 = requests.get(md_diabetes)
md_diabetes_data = response3.json()

df3 = pd.DataFrame(md_diabetes_data)
df3.info()
print(df3.head())

df3['data_value'] = pd.to_numeric(df3['data_value'])
avg_md = df3['data_value'].mean()
print(avg_md)

avg_va = df['data_value'].mean()
print(avg_va)

comparison_df = pd.DataFrame({'state': ['Virginia', 'Maryland'], 'avg_diabetes_prevalence': [avg_va, avg_md]})
print(comparison_df)

plt.figure(figsize = (6, 5))
sns.barplot(data = comparison_df, x = 'state', y = 'avg_diabetes_prevalence', palette = 'OrRd')
plt.title('Average Diabetes Prevalence by State (2021)')
plt.xlabel ('State')
plt.ylabel('Diabetes Prevalence (%)')
plt.ylim(0, max(avg_va, avg_md) + 2)
plt.show()

md_va_merged = pd.concat([df, df3])
print(md_va_merged)
md_va_merged.info()

plt.figure(figsize = (5, 7))
sns.boxplot(data = md_va_merged, x = 'stateabbr', y = 'data_value', palette = 'OrRd')
plt.title('Diabetes Prevalence Distribution By State (2021)')
plt.ylabel('Diabetes Prevalence (%)')
plt.xlabel ('State')
plt.show()