# importing data set
import pandas as pd

df = pd.read_csv('gcc-jodi-oil-dataset.csv', sep=';')
#Displaying the First 5 Rows
print(df.head())
print(df.index)

#Displaying the Dimensions of the Dataset
print("Number of Original Rows:",df.shape[0])
print("Number of Original Columns:",df.shape[1])

#FIltering the data to analyze data from 2021 to 2025
df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'])
df_filtered = df[df['TIME_PERIOD'] >= '2021-01-01']


print("Number of filtered Rows:",df_filtered.shape)

# checking nul values
print(df_filtered.isnull().sum())
null_rows = df_filtered[df_filtered['OBS_VALUE'].isnull()]
print(null_rows.head())
print(null_rows['FLOW_BREAKDOWN'].value_counts())
print(null_rows['AREA'].value_counts())

selected_flows = [
    'Production',
    'Imports',
    'Exports',
    'Refinery output',
    'Demand'
]

df_filtered_flows = df_filtered[df_filtered['FLOW_BREAKDOWN'].isin(selected_flows)].copy()

countries = df_filtered_flows['AREA'].unique()

df_list = []

for country in countries:
    df_temp = df_filtered_flows[df_filtered_flows['AREA'] == country].copy()

    # drop missing values
    df_temp = df_temp.dropna(subset=['OBS_VALUE'])

    # sort properly
    df_temp = df_temp.sort_values(
        ['ENERGY_PRODUCT_NAME','FLOW_BREAKDOWN','UNIT_MEASURE','TIME_PERIOD']
    )

    # previous value
    df_temp['Previous_OBS'] = df_temp.groupby(
        ['ENERGY_PRODUCT_NAME','FLOW_BREAKDOWN','UNIT_MEASURE']
    )['OBS_VALUE'].shift(1)

    # growth formula
    df_temp['Growth_Percentage'] = (
        (df_temp['OBS_VALUE'] - df_temp['Previous_OBS']) /
        df_temp['Previous_OBS']
    ) * 100

df_list.append(df_temp)

df_final = pd.concat(df_list)

df_final = df_final.replace([float('inf'), -float('inf')], None)
df_final = df_final.dropna(subset=['Growth_Percentage'])

#add new columns for Year, Quarter and MOnth name
df_final['Year'] = df_final['TIME_PERIOD'].dt.year
df_final['Quarter'] = df_final['TIME_PERIOD'].dt.quarter
df_final['Month_Name'] = df_final['TIME_PERIOD'].dt.month_name()

#add new column for Pru=oduction Categories

production_map = {
    'Production': 'Production',
    'Refinery output': 'Production',
    'Refinery intake': 'Production',

    'Imports': 'Trade',
    'Exports': 'Trade',
    'Receipts': 'Trade',
    'Products transferred': 'Trade',

    'Demand': 'Demand',
    'Direct use': 'Demand',

    'Closing stocks': 'Inventory',
    'Stock change': 'Inventory',
    'Statistical difference': 'Inventory'
}
df_final['Production_Category'] = df_final['FLOW_BREAKDOWN'].map(production_map)


print(df_final.tail(20).to_string())
