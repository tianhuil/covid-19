import time
from contextlib import contextmanager

import pandas as pd
import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
matplotlib.rcParams['figure.figsize'] = 12, 6
matplotlib.rcParams['font.size'] = 18  # Probably OS Dependent

@contextmanager
def loading(data_source):
    loading = st.text(f'Loading {data_source} ...')
    yield
    loading.text(f'Loading {data_source} ... Done!')

@st.cache
def load_wa_data(day):
    US_DIR = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    df_whole = pd.read_csv(US_DIR)

    df = df_whole.loc[df_whole['state'] == 'Washington', :].set_index('date')
    df.loc[:, 'delta_cases'] = df['cases'] - df['cases'].shift()
    return df

@st.cache
def load_king_data(day):
    US_DIR = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    df_whole = pd.read_csv(US_DIR)

    df = df_whole[(df_whole['state'] == 'Washington') & (df_whole['county'] == 'King')].set_index('date')
    df.loc[:, 'delta_cases'] = df['cases'] - df['cases'].shift()
    return df

def plot_df(df):
    series = df.set_index('cases')['delta_cases']
    pd.DataFrame({
        'rolling-7': series.rolling(7).mean(),
        'ewm-7': series.ewm(7).mean(),
        'new cases': series,
    }).plot(loglog=True)
    st.pyplot()

# days since epoch
day = (time.time() // (24 * 60 * 60))

with loading('Washington State Data'):
    df = load_wa_data(day)
st.header('Washington State Log-Log Plot')
plot_df(df)


with loading('King County Data'):
    df = load_king_data(day)
st.header('King County Log-Log Plot')
plot_df(df)
