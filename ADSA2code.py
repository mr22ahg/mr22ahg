import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_wb_data(filePath):
    """
     Read WB data and return dataframe. Drops unnecessary columns and pivot tables
     
     @param filePath - Path to CSV file to read
     
     @return DataFrame with country and industry codes as columns
    """
    # read CSV file and skip first four rows
    df = pd.read_csv(filePath, skiprows=4)

    # drop unnecessary columns
    df = df.drop(columns=['Country Code', 'Indicator Code', 'Unnamed: 66'])

    # melt the dataframe to long format
    df = df.melt(id_vars=['Country Name', 'Indicator Name'], var_name='Year', value_name='Value')
    df = df.pivot_table(values='Value', columns='Indicator Name', index=['Country Name', 'Year']).reset_index()

    # drop null values
    df = df.dropna(thresh=int(0.25 * df.shape[0]), axis=1)
    df = df.dropna(thresh=int(0.25 * df.shape[1]))

    # convert years to columns
    df_years = df.set_index(['Year', 'Country Name']).unstack(level=0).swaplevel(axis=1).sort_index(axis=1, level=0)

    # convert countries to columns
    df_countries = df.set_index(['Year', 'Country Name']).unstack(level=1).swaplevel(axis=1).sort_index(axis=1, level=0)
    
    return df_years, df_countries

countries = ['Europe & Central Asia', 'India', 'United Kingdom', 'Australia', 'Germany', 'Russian Federation']
indicators = [
    'Renewable electricity output (% of total electricity output)',
    'Urban population (% of total population)',
    'Total greenhouse gas emissions (% change from 1990)',
    'Rural population living in areas where elevation is below 5 meters (% of total population)',
    'Urban population',
    'Electricity production from nuclear sources (% of total)',
    'Agricultural land (% of land area)',
    'Energy use (kg of oil equivalent) per $1,000 GDP (constant 2017 PPP)',
    'Electricity production from oil sources (% of total)'
    ]

df_years, df_countries = read_wb_data("worldBankData.csv")

# Reset index to default. This is useful for debugging and to avoid having to re - index
df = df_countries.unstack().unstack(level=1).reset_index()

# Plot correlation matrix for United Kingdom. This is a heatmap with annotation
xticks=yticks=[i for i in df.columns.to_list() if i in indicators]
ax = sns.heatmap(df_countries['United Kingdom'][xticks].corr(), annot=True)
ax.set_title("Correlation Matrix for United Kingdom")
ax.set_xlabel(''), ax.set_ylabel(''), ax.set_xticklabels(xticks, fontsize=8), ax.set_yticklabels(yticks, fontsize=8)
plt.savefig('ukCorr.png')

# Plot agricultural land for each year. This is a barplot with one column for each country
plt.figure(figsize=(6, 4))
ax = sns.barplot(x = 'Country Name', y = "Agricultural land (% of land area)", hue = 'Year',
                data = df_years[list(map(str, range(1990, 2016, 5)))].loc[countries].unstack().unstack(level=1).reset_index()
                )
ax.set_ylabel(''), ax.set_xlabel(''), ax.set_title("Agricultural land (% of land area)", fontsize=6)
ax.set_xticklabels(countries, fontsize=8)
plt.savefig('agriBarPlot.png')


# Plot barplot of Renewable Electricity outputs for each year
plt.figure(figsize=(6,4))
ax = sns.barplot(x = 'Country Name', y = "Renewable electricity output (% of total electricity output)", hue = 'Year',
                data = df_years[list(map(str, range(1990, 2016, 5)))].loc[countries].unstack().unstack(level=1).reset_index()
                )
ax.set_ylabel(''), ax.set_xlabel(''), ax.set_title("Renewable electricity output (% of total electricity output)", fontsize=6)
ax.set_xticklabels(countries, fontsize=8)
plt.legend(loc='upper left', fontsize=6)
plt.savefig('reBarPlot.png')


# create a new column for access to electricity categories
df[f"cat_Urban population"] = pd.cut(df["Urban population"], bins=[0, 25, 50, 75, 100], labels=['Very Low', 'Low', 'Medium', 'High'])

# create a horizontal bar plot
plt.figure(figsize=(4,3))
ax = sns.barplot(x="Renewable electricity output (% of total electricity output)", y=f"cat_Urban population", data=df[df['Country Name'].isin(countries)], hue='Country Name')
plt.legend(loc='upper right', fontsize=6)
plt.savefig('cat.png')


# create a multiple line plot
plt.figure(figsize=(4,3))
ax = sns.lineplot(x='Year', y="Electricity production from nuclear sources (% of total)", hue='Country Name', 
                  data=df[df['Country Name'].isin(countries) & df['Year'].isin(list(map(str, range(1990, 2016, 5))))], dashes=True)
# Set the linestyle to the dashed line style
for i in ax.lines:
    i.set_linestyle("--")
# Set the label for the electricity production plot.
ax.set_ylabel(ylabel='')
ax.set_title("Electricity production from nuclear sources (% of total)", fontsize=8)
plt.legend(loc='upper left', fontsize='6')
plt.savefig('lp.png')


# create a multiple line plot
plt.figure(figsize=(4,3))
ax = sns.lineplot(x='Year', y="Total greenhouse gas emissions (% change from 1990)", hue='Country Name', 
                  data=df[df['Country Name'].isin(countries) & df['Year'].isin(list(map(str, range(1990, 2016, 5))))], dashes=True)
# Set the linestyle to the dashed line style
for i in ax.lines:
    i.set_linestyle("--")
# Set the label for the greenhouse plot.
ax.set_ylabel(ylabel='')
ax.set_title("Total greenhouse gas emissions (% change from 1990)", fontsize=8)
plt.legend(loc='upper left', fontsize='6')
plt.savefig('lp1.png')

# Add years from 1995 to 2005 and 2015 to df. csv droplevel
newDf = df_years[[('1995', "Urban population"), ('2005', "Urban population"), ('2015', "Urban population")]].loc[countries]
newDf.columns = newDf.columns.droplevel(1)
newDf.to_csv('df.csv')

# Plot cross - tab plot of Renewable electricity output and country
pd.crosstab(pd.cut(df[df['Country Name'].isin(countries)]['Renewable electricity output (% of total electricity output)'], 10), df[df['Country Name'].isin(countries)]['Country Name']).plot.bar(stacked=True)
