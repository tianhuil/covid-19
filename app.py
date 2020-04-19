import io
from flask import Flask, Response, render_template
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
matplotlib.rcParams['figure.figsize'] = 12, 6
matplotlib.rcParams['font.size'] = 18  # Probably OS Dependent

import pandas as pd

app = Flask(__name__, template_folder='templates')

def load_wa_data():
    US_DIR = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    df_whole = pd.read_csv(US_DIR)

    df = df_whole.loc[df_whole['state'] == 'Washington', :].set_index('date')
    df.loc[:, 'delta_cases'] = df['cases'] - df['cases'].shift()
    return df

def load_king_data():
    US_DIR = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    df_whole = pd.read_csv(US_DIR)

    df = df_whole[(df_whole['state'] == 'Washington') & (df_whole['county'] == 'King')].set_index('date')
    df.loc[:, 'delta_cases'] = df['cases'] - df['cases'].shift()
    return df

def plot_df(df, ax):
    series = df.set_index('cases')['delta_cases']
    pd.DataFrame({
        'rolling-7': series.rolling(7).mean(),
        'ewm-7': series.ewm(7).mean(),
        'new cases': series,
    }).plot(loglog=True, ax=ax)

def create_figure(df):
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    plot_df(df, ax)
    return fig

def plot_png_raw(df):
    df = load_wa_data()
    fig = create_figure(df)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output.getvalue()

def plot_png_base64(df):
    output = plot_png_raw(df)
    return base64.encodestring(output).decode('utf8')

@app.route('/wa.png')
def plot_wa():
    df = load_wa_data()
    output = plot_png_raw(df)
    return Response(output, mimetype='image/png')

@app.route('/king.png')
def plot_king():
    df = load_king_data()
    output = plot_png_raw(df)
    return Response(output, mimetype='image/png')

@app.route('/')
def index():
    wa_df = load_wa_data()
    wa_png = plot_png_base64(wa_df)
    wa_tail = wa_df.tail().to_html()

    king_df = load_king_data()
    king_png = plot_png_base64(king_df)
    king_tail = king_df.tail().to_html()

    return render_template('index.html',
        wa_png=wa_png,
        wa_tail=wa_tail,
        king_png=king_png,
        king_tail=king_tail,
    )

if __name__ == '__main__':
    app.run()
