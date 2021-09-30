# -*- coding: utf-8 -*-
"""world_bank_population.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1f5j8kacwOd_dZqxoO_XCtwuk2jck67bz
    
final csv file:
https://drive.google.com/file/d/1YY8ewSuZD-wx9qJNdvjmz9MB0qJxP-7L/view?usp=sharing&resourcekey=0-ncNblwybOhMGrC2IFPDf_w
"""

import requests
import pandas as pd

AGES = 26

series  = [f"SP.POP.AG{age:02d}.{gender}.IN" for age in range(AGES)
           for gender in ['FE', 'MA']]

def get_df(serieses):
    '''
    gets df by iteratively running code for each country + series
    '''
    df2 = pd.DataFrame
    df2 = pd.DataFrame(columns = ['Series Name', 'Series Code', 'Country Code', 'Country',
                                  'Year', 'Value'])
    current_series = "&".join(serieses)
    MAX_PER_PAGE = 32767 
    # maximum that can be displayed per page according to API rules
    #will not need to change this, well within reasonable limits
    url = f"https://api.worldbank.org/v2/country/all/indicator/{current_series}?"
    url = url + f"format=JSON&per_page={MAX_PER_PAGE}"
    print(url)

    response = requests.get(url)
    response = response.json()
    for counter in range(len(response[1])):
        val = response[1][counter]['value']
        if val is not None:
            row = {"Series Name" : response[1][counter]['indicator']['value'],
                "Series Code" : response[1][counter]['indicator']['id'],
                "Country Code" : response[1][counter]['countryiso3code'],
                "Country" : response[1][counter]['country']['value'],
                "Year" : response[1][counter]['date'],
                'Value' : response[1][counter]['value']

                }
            df2.loc[len(df2)] = row
    return df2

def get_mcf(series_lst):
    '''
    gets mcf by splitting description and using fstrings
    '''
    nodes = []
    with open("World_bank_hnp_population.mcf", 'w', encoding = 'utf-8') as file:
        mcf = ''
        for current_series in series_lst:
            print('\n'+current_series)
            statvars = ['Node', 'typeOf', 'description', 'populationType',
                      'measuredProperty', 'gender', 'statType', 'age']
            node, age, gender = '', '', ''
            age = current_series[9:11]
            gender = ''
            if 'MA' in current_series:
                gender = 'Male'
            else:
                gender = 'Female'
            node = f'Count_Persons_{(int(age))}Years_{gender}'
            desc = f'Age population, age {age}, {gender.lower()}, interpolated'
            nodes.append(node)
            values = [node, 'dcs:StatisticalVariable', f'"{desc}"',
                    'dcs:Person', 'dcs:count', f'dcs:{gender}',
                    'dcs:measuredValue', f'[Years {age}]']
            req_len = len(statvars)
            for i in range(req_len):
                mcf = mcf + f'{statvars[i]}: {values[i]}\n'
            mcf = mcf + '\n'

        file.write(mcf)

def get_statvars(gender, age):
    from util import statvar_dcid_generator
    statvars = ['typeOf', 'description', 'populationType',
                'measuredProperty', 'gender', 'statType', 'age']
    values = ['dcs:StatisticalVariable', 
              f'Age population, {gender}, Age {age}, interpolated',
              'dcs:Person', 'dcs:count', f'dcs:{gender}',
              'dcs:measuredValue', f'[Years {age}]']
    file = dict()
    for i in range(len(statvars)):
        file[statvars[i]] = values[i]
    dcid = statvar_dcid_generator.get_stat_var_dcid(file)
    return dcid
    
def get_csv(df_in):
    """Creation of csv according to tmcf:"""
    df2 = pd.DataFrame(columns = ['Country', 'Year', "StatVar", 'Population'])
    for line in range(len(df)):
        gender, statvar = '', ''
        gender = df_in['Series Name'][line].split(',')[-2].strip()
        gender = gender[0].upper() + gender[1:]
        age = df_in['Series Name'][line].split(',')[-1].strip()
        statvar = get_statvars(gender, age)'
        addto_df2 = [df['Country'][line], df['Year'][line], statvar,
                                   df['Value'][line]]
        df2.loc[len(df2.index)] = addto_df2
    df2.to_csv("WorldBankPopulation.csv")

get_mcf(series)
df = get_df(series)
get_csv(df)
