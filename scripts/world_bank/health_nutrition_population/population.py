import requests
import pandas as pd
from absl import app
from absl import flags
#from util import statvar_dcid_generator


FLAGS = flags.FLAGS
flags.DEFINE_integer("age", 2,
                     "Age to which this program is run, max value 26")
flags.DEFINE_string("gender", "FE MA", "Gender: FE for female, MA for male")
flags.DEFINE_string("country", "USA", "Country codes")
#maximum the API Can display is 32767
flags.DEFINE_integer("per_page", 32, "rows per page")
flags.DEFINE_string("path", "WorldBankHNP_Population_Tests.csv", "Path of final csv")




def get_df(serieses, per_page, country):
    '''
    gets df by iteratively running code for each country + series
    '''
    df2 = pd.DataFrame
    df2 = pd.DataFrame(columns = ['Series Name', 'Series Code', 'Country Code', 'Country',
                                  'Year', 'Value'])
    for current_series in serieses:
        # maximum that can be displayed per page according to API rules
        #will not need to change this in the forseeable future
        MAX_PER_PAGE = 32767
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{current_series}?"
        url = url + f"format=JSON&per_page={per_page}"
        response = requests.get(url)
        response = response.json()
        for counter in range(len(response[1])):
            row = 0
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

def get_statvars(gender, age):
    property_dict = {'typeOf': 'dcs:StatisticalVariable',
                     'description': f'Age population, {gender}, Age {age}, interpolated',
                     'populationType': 'dcs:Person', 'measuredProperty':
                     'dcs:count','gender': 'dcs:{gender}',
                     'statType': 'dcs:measuredValue', 'age': '[Years {age}]'}
    dcid = statvar_dcid_generator.get_stat_var_dcid(property_dict)
    return (dcid)

def get_csv(df_in, df_out_path):
    """Creation of csv according to tmcf:"""
    df2 = pd.DataFrame(columns = ['Country', 'Year', "StatVar", 'Population'])
    for line in range(len(df_in)):
        gender, statvar = '', ''
        gender = df_in['Series Name'][line].split(',')[-2].strip()
        gender = gender[0].upper() + gender[1:]
        age = df_in['Series Name'][line].split(',')[-1].strip()
        statvar = get_statvars(gender, age)
        addto_df2 = [df['Country'][line], df['Year'][line], statvar,
                                   df['Value'][line]]
        df2.loc[len(df2.index)] = addto_df2
    df2.to_csv(df_out_path)
    
def main(argv):
    series  = [f"SP.POP.AG{age:02d}.{gender}.IN" for age in range(FLAGS.age)
               for gender in (FLAGS.gender.split())]
    df = get_df(series, FLAGS.per_page, FLAGS.country)
    get_csv(df, FLAGS.path)
   
app.run(main)
