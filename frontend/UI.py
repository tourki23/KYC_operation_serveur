import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import numpy as np
import requests # <-- Nécessaire pour envoyer l'ordre à l'API

# --- CONNEXION À L'ORM POSTGRESQL ---
try:
    # Pour le local (depuis la racine)
    from .ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog
except (ImportError, ValueError):
    # Pour Docker (où le fichier est à la racine /app)
    from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog

# --- CONFIGURATION COULEURS OPS ---
C_GREEN = "#2ecc71"  # Approved / Sain
C_ORANGE = "#f39c12" # Watch / Suspect
C_RED = "#e74c3c"    # Blocked / Fraudeur
DARK_PURE = "#000000"
DARK_CARD = "#111111"

# --- CONFIGURATION DE L'URL API (FORCE RENDER) ---
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

# Petit nettoyage au cas où il y aurait un / à la fin
if API_URL.endswith('/'):
    API_URL = API_URL[:-1]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)

# --- CHARGEMENT DES MÉTRIQUES (COMPARATIF) ---
def load_metrics(model_name):
    try:
        with open(f"models/{model_name}_metrics.json", "r") as f:
            return json.load(f)
    except:
        return {}

m_xgb = load_metrics("XGBoost")
m_log = load_metrics("LogisticRegression")

# --- CHARGEMENT DATA CLIENTS VIA ORM ET GÉNÉRATION DU GRAPH MACRO ---
db = SessionLocal()
try:
    query_clients = db.query(Client).all()
    if query_clients:
        DF_CLIENTS_STATIC = pd.DataFrame([u.__dict__ for u in query_clients]).drop(columns=['_sa_instance_state'], errors='ignore')
        DF_CLIENTS_STATIC['client_id'] = DF_CLIENTS_STATIC['client_id'].astype(str)
        
        dropdown_options = [{'label': f"ID: {r['client_id']} - {r['pays_residence']}", 'value': str(r['client_id'])} for _, r in DF_CLIENTS_STATIC.iterrows()]
        
        df_macro = DF_CLIENTS_STATIC['profil_risque'].value_counts(normalize=True).reset_index()
        df_macro.columns = ['profil', 'percentage']
        df_macro['percentage'] *= 100
        df_macro['label_text'] = df_macro.apply(lambda r: f"{r['profil']}: {r['percentage']:.1f}%", axis=1)
        df_macro['profil_clean'] = df_macro['profil'].astype(str).str.lower().str.strip()

        fig_macro = px.bar(df_macro, x='percentage', y='profil', orientation='h',
                           color='profil_clean', 
                           color_discrete_map={
                               'normal': C_GREEN, 'standard': C_GREEN, 
                               'vigilance': C_ORANGE, 'suspect': '#e74c3c', 
                               'ppe': '#c0392b', 'fraudeur': '#641e16'
                           },
                           template="plotly_dark", text='label_text') 
        
        fig_macro.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, showlegend=False,
                                xaxis_title="Pourcentage (%)", yaxis_title=None, yaxis={'categoryorder':'total ascending'},
                                xaxis_ticksuffix="%", margin=dict(l=10, r=60, t=10, b=10))
        fig_macro.update_traces(textposition='outside', cliponaxis=False)

    else:
        DF_CLIENTS_STATIC = pd.DataFrame()
        fig_macro = go.Figure()

except Exception as e:
    print(f"ERREUR CHARGEMENT : {e}")
    DF_CLIENTS_STATIC = pd.DataFrame()
    fig_macro = go.Figure()
finally:
    db.close()

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}<title>KYC - OPS CENTER</title>{%favicon%}{%css%}
        <style>
            body { background-color: #000000 !important; font-family: 'Segoe UI', sans-serif; color: white; margin: 0; padding: 0; }
            .xtab { background-color: #080808 !important; color: #fff !important; border: none !important; }
            .xtab--selected { background-color: #003399 !important; font-weight: bold !important; border-bottom: 3px solid #0056b3 !important; }
            .dash-spreadsheet-container .dash-spreadsheet-inner tr { background-color: #000000 !important; }
            .dash-spreadsheet-container .dash-spreadsheet-inner td { background-color: #000000 !important; }
            .card { background-color: #111111 !important; border: 1px solid #333 !important; }
            .card-stats { background-color: #111111 !important; border: 1px solid #333 !important; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
            .metric-val { font-weight: bold; color: #ffffff; }
        </style>
    </head>
    <body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
'''

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("KYC - OPERATIONS CENTER ", className="text-white", style={'fontWeight': 'bold'}), width=7),
        dbc.Col(
            html.Div([
                html.Span("Developed by Mahmoud TOURKI", className="text-muted", style={'fontSize': '14px', 'marginRight': '15px'}),
                html.A(html.Img(src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg", style={'height': '25px', 'marginRight': '15px'}), href="mailto:mahmoud.tourki24@gmail.com"),
                html.A(html.Img(src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg", style={'height': '25px'}), href="https://www.linkedin.com/in/mahmoud-tourki", target="_blank")
            ], className="d-flex justify-content-end align
