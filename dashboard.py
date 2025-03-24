# Importer les bibliothèques nécessaires
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

# Connexion à la base SQLite
conn = sqlite3.connect('C:/Users/Cedoque BAGBONON/Documents/PRO/bank_marketing.db')  # Remplacez par votre chemin

# Charger les données
df = pd.read_sql_query("""
    SELECT c.*, ca.contact, ca.month, ca.day_of_week, ca.duration, ca.campaign, 
           ca.pdays, ca.previous, ca.poutcome, ca.y
    FROM Clients c
    JOIN Campagnes ca ON c.ID_Client = ca.ID_Client
""", conn)
conn.close()

# Convertir 'y' en 0/1 pour les calculs
df['y_numeric'] = df['y'].map({'yes': 1, 'no': 0})

# Initialiser l'application Dash
app = Dash(__name__)

# Définir les options pour les filtres
age_groups = sorted(df['age_group'].unique())
months = sorted(df['month'].unique())
jobs = sorted(df['job'].unique())
maritals = sorted(df['marital'].unique())
educations = sorted(df['education'].unique())
housings = sorted(df['housing'].unique())

# Mise en page du dashboard avec styles CSS
app.layout = html.Div([
    # Titre principal avec style
    html.H1("Dashboard Interactif : Analyse des Campagnes Marketing", 
            style={'textAlign': 'center', 'color': '#FFFFFF', 'padding': '20px', 
                   'backgroundColor': '#2C3E50', 'marginBottom': '30px'}),

    # Section des filtres
    html.Div([
        # Conteneur des filtres avec style
        html.Div([
            html.Label("Filtrer par groupe d'âge :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='age-group-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in age_groups],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
            html.Label("Filtrer par mois :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='month-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in months],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
            html.Label("Filtrer par profession :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='job-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in jobs],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
            html.Label("Filtrer par état civil :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='marital-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in maritals],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
            html.Label("Filtrer par niveau d'éducation :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='education-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in educations],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
            html.Label("Filtrer par logement (housing) :", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='housing-filter',
                options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': x, 'value': x} for x in housings],
                value='Tous',
                multi=False,
                style={'backgroundColor': '#ECF0F1', 'color': '#000000', 'marginBottom': '15px'}
            ),
        ], style={'width': '30%', 'margin': 'auto', 'backgroundColor': '#34495E', 'padding': '20px', 
                  'borderRadius': '10px', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.3)'}),
    ], style={'backgroundColor': '#2C3E50', 'padding': '20px'}),

    # Section des graphiques
    html.Div([
        dcc.Graph(id='subscription-by-age-group', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='subscription-by-month', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='duration-by-subscription', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='distribution-by-job', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='job-age-subscription', style={'width': '100%'}),
        dcc.Graph(id='subscription-by-job-rate', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='marital-distribution', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='education-distribution', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='housing-distribution', style={'width': '50%', 'display': 'inline-block'}),
    ], style={'backgroundColor': '#2C3E50', 'padding': '20px'}),
    
    # Section Conseils Marketing
    html.H2("Conseils Marketing", style={'textAlign': 'center', 'color': '#FFFFFF', 'padding': '20px'}),
    html.Ul(id='marketing-tips', style={'fontSize': 16, 'margin': '20px', 'color': '#ECF0F1'}),
], style={'backgroundColor': '#2C3E50', 'minHeight': '100vh'})

# Callback pour mettre à jour les graphiques et conseils
@app.callback(
    [Output('subscription-by-age-group', 'figure'),
     Output('subscription-by-month', 'figure'),
     Output('duration-by-subscription', 'figure'),
     Output('distribution-by-job', 'figure'),
     Output('job-age-subscription', 'figure'),
     Output('subscription-by-job-rate', 'figure'),
     Output('marital-distribution', 'figure'),
     Output('education-distribution', 'figure'),
     Output('housing-distribution', 'figure'),
     Output('marketing-tips', 'children')],
    [Input('age-group-filter', 'value'),
     Input('month-filter', 'value'),
     Input('job-filter', 'value'),
     Input('marital-filter', 'value'),
     Input('education-filter', 'value'),
     Input('housing-filter', 'value')]
)
def update_dashboard(selected_age_group, selected_month, selected_job, selected_marital, selected_education, selected_housing):
    # Filtrer les données selon les sélections
    filtered_df = df.copy()
    if selected_age_group != 'Tous':
        filtered_df = filtered_df[filtered_df['age_group'] == selected_age_group]
    if selected_month != 'Tous':
        filtered_df = filtered_df[filtered_df['month'] == selected_month]
    if selected_job != 'Tous':
        filtered_df = filtered_df[filtered_df['job'] == selected_job]
    if selected_marital != 'Tous':
        filtered_df = filtered_df[filtered_df['marital'] == selected_marital]
    if selected_education != 'Tous':
        filtered_df = filtered_df[filtered_df['education'] == selected_education]
    if selected_housing != 'Tous':
        filtered_df = filtered_df[filtered_df['housing'] == selected_housing]

    # Graphique 1 : Taux de souscription par groupe d'âge
    age_group_sub = filtered_df.groupby('age_group')['y_numeric'].mean().reset_index()
    fig1 = px.bar(age_group_sub, x='age_group', y='y_numeric',
                  labels={'y_numeric': 'Taux de souscription', 'age_group': "Groupe d'âge"},
                  title="Taux de souscription par groupe d'âge")

    # Graphique 2 : Taux de souscription par mois
    month_sub = filtered_df.groupby('month')['y_numeric'].mean().reset_index()
    month_order = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    month_sub['month'] = pd.Categorical(month_sub['month'], categories=month_order, ordered=True)
    month_sub = month_sub.sort_values('month')
    fig2 = px.bar(month_sub, x='month', y='y_numeric',
                  labels={'y_numeric': 'Taux de souscription', 'month': 'Mois'},
                  title="Taux de souscription par mois")

    # Graphique 3 : Durée des appels selon souscription
    fig3 = px.box(filtered_df, x='y', y='duration',
                  labels={'y': 'Souscription (yes/no)', 'duration': 'Durée (secondes)'},
                  title="Durée des appels selon la souscription")

    # Graphique 4 : Distribution des professions
    fig4 = px.histogram(filtered_df, x='job', title="Distribution des professions",
                        labels={'job': 'Profession', 'count': 'Nombre'},
                        category_orders={'job': jobs})
    fig4.update_layout(xaxis={'tickangle': 45})

    # Graphique 5 : Distribution des professions par groupe d'âge et souscription
    fig5 = px.histogram(filtered_df, x='job', color='y', facet_col='age_group',
                        title="Distribution des professions par groupe d'âge et souscription",
                        labels={'job': 'Profession', 'count': 'Nombre'},
                        category_orders={'job': jobs})
    fig5.update_layout(xaxis={'tickangle': 45})

    # Graphique 6 : Taux de souscription par profession
    job_sub_rate = filtered_df.groupby('job')['y_numeric'].mean().reset_index()
    fig6 = px.bar(job_sub_rate, x='job', y='y_numeric',
                  labels={'y_numeric': 'Taux de souscription', 'job': 'Profession'},
                  title="Taux de souscription par profession")
    fig6.update_layout(xaxis={'tickangle': 45})

    # Graphique 7 : Distribution de l'état civil
    fig7 = px.histogram(filtered_df, x='marital', color='y',
                        title="Distribution de l'état civil par souscription",
                        labels={'marital': "État civil", 'count': 'Nombre'})
    fig7.update_layout(xaxis={'tickangle': 45})

    # Graphique 8 : Distribution de l'éducation
    fig8 = px.histogram(filtered_df, x='education', color='y',
                        title="Distribution de l'éducation par souscription",
                        labels={'education': "Niveau d'éducation", 'count': 'Nombre'})
    fig8.update_layout(xaxis={'tickangle': 45})

    # Graphique 9 : Distribution de housing
    fig9 = px.histogram(filtered_df, x='housing', color='y',
                        title="Distribution du logement (housing) par souscription",
                        labels={'housing': "Logement", 'count': 'Nombre'})
    fig9.update_layout(xaxis={'tickangle': 45})

    # Conseils marketing dynamiques
    tips = [
        html.Li("Cibler les seniors (61+) et les jeunes (0-25) avec des appels longs (>500s) pour maximiser les souscriptions."),
        html.Li(f"Concentrer les campagnes en {', '.join(['mars', 'septembre', 'décembre'])}, où les taux sont les plus élevés."),
        html.Li("Prioriser la profession 'retired', qui montre un fort potentiel de conversion."),
        html.Li("Relancer rapidement les clients avec plusieurs contacts précédents (previous > 0) pour améliorer l'efficacité."),
    ]
    if selected_age_group != 'Tous' and filtered_df['y_numeric'].mean() > 0.2:
        tips.append(html.Li(f"Augmenter les efforts sur le groupe d'âge {selected_age_group} qui affiche un taux de souscription élevé."))

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, tips

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)