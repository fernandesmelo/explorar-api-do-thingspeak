from flask import Flask, render_template
import requests
import pandas as pd
import plotly.graph_objs as go

app = Flask(__name__)

# Configurações
THINGSPEAK_CHANNEL_ID = 'SEU_CHANNEL_ID'
THINGSPEAK_API_KEY = 'SEU_API_KEY'  # Deixe vazio '' se o canal for público
NUM_RESULTS = 100
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"


def get_thingspeak_data():
    params = {
        'results': NUM_RESULTS
    }
    if THINGSPEAK_API_KEY:
        params['api_key'] = THINGSPEAK_API_KEY

    response = requests.get(THINGSPEAK_URL, params=params)
    if response.status_code != 200:
        return None, "Erro ao acessar a API do ThingSpeak"

    data = response.json()['feeds']
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['umidade'] = pd.to_numeric(df['field1'], errors='coerce')
    df['temperatura'] = pd.to_numeric(df['field2'], errors='coerce')
    df.dropna(subset=['umidade', 'temperatura'], inplace=True)
    return df, None


@app.route('/')
def index():
    df, error = get_thingspeak_data()
    if error:
        return f"<h1>{error}</h1>"

    # Últimos valores
    last_temp = df['temperatura'].iloc[-1]
    last_umidade = df['umidade'].iloc[-1]

    # Gráficos interativos com Plotly
    temp_trace = go.Scatter(x=df['created_at'], y=df['temperatura'], mode='lines+markers', name='Temperatura (°C)')
    umidade_trace = go.Scatter(x=df['created_at'], y=df['umidade'], mode='lines+markers', name='Umidade (%)')

    temp_graph = go.Figure(data=[temp_trace])
    temp_graph.update_layout(title='Temperatura', xaxis_title='Data', yaxis_title='°C')

    umidade_graph = go.Figure(data=[umidade_trace])
    umidade_graph.update_layout(title='Umidade', xaxis_title='Data', yaxis_title='%')

    temp_div = temp_graph.to_html(full_html=False)
    umidade_div = umidade_graph.to_html(full_html=False)

    return render_template("index.html",
                           last_temp=last_temp,
                           last_umidade=last_umidade,
                           temp_plot=temp_div,
                           umidade_plot=umidade_div)


if __name__ == '__main__':
    app.run(debug=True)
