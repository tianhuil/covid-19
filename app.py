import datetime
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
    start = datetime.datetime.now()
    yield
    end = datetime.datetime.now()
    loading.text(f'Loading {data_source} ... Done in {(end - start).total_seconds()} seconds!')

def plot_df(df):
    series = df.set_index('cases')['delta_cases']
    fig, ax = plt.subplots()
    pd.DataFrame({
        'new cases': series,
        'rolling-7': series.rolling(7).mean(),
        'ewm-7': series.ewm(6).mean(),
    }).reindex(columns=['new cases', 'rolling-7', 'ewm-7']).plot(loglog=True, ax=ax)
    st.pyplot(fig)

def select_column(df, col, default=None, key=None):
    states = sorted(df[col].unique())
    if default:
        default_index = states.index(default)
        option = st.selectbox(f'Select {col}', states,  default_index, key=key)
    else:
        option = st.selectbox(f'Select {col}', states, key=key)
    return option, df[df[col] == option]


@st.cache
def load_data(file):
    US_DIR = f'https://raw.githubusercontent.com/nytimes/covid-19-data/master/{file}'
    return pd.read_csv(US_DIR)

with loading('State Data'):
    df = load_data('us-states.csv')

state, df_state = select_column(df, 'state', default='Washington', key=1)

df_state = df_state.set_index('date')
df_state.loc[:, 'delta_cases'] = df_state['cases'] - df_state['cases'].shift()
st.header(f'{state} State Log-Log Plot')
plot_df(df_state)


with loading('County Data'):
    df = load_data('us-counties.csv')

state, df_state = select_column(df, 'state', default='Washington', key=2)
county, df_county = select_column(df_state, 'county', default='King' if state == 'Washington' else None, key=3)

df_county = df_county.set_index('date', 'state')
df_county.loc[:, 'delta_cases'] = df_county['cases'] - df_county['cases'].shift()
st.header(f'{state}, {county} State Log-Log Plot')
plot_df(df_county)
