from pymongo import MongoClient
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
import sqlite3

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client["twitter_analysis"]
collection = db["data"]

all_records = collection.find()
list_cursor = list(all_records)
df = pd.DataFrame(list_cursor)

###################### PREMIER GRAPH 

sentiment_data = collection.distinct("sentiment_class")
# Préparation des données pour le graphique en cercle
labels = sentiment_data
sizes = [collection.count_documents({"sentiment_class": sentiment}) for sentiment in sentiment_data]

# Création du graphique en cercle interactif
fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3)])

# Mise en forme du graphique
fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=15,
                  marker=dict(colors=['red', 'yellow', 'green'], line=dict(color='#000000', width=2)))

# Titre du graphique
fig.update_layout(
    title={
        'text': "Tweets par sentiment",
        'x': 0.5,
        'y': 0.9,
        'xanchor': 'center',
        'yanchor': 'middle',
        'font': {'color': 'white'}
    },
    paper_bgcolor='rgba(22, 35, 49, 0.966)',
    plot_bgcolor='rgba(22, 35, 49, 0.966)',
    font_color='white'
)

# Enregistrer le graphique en tant que fichier HTML
fig.write_html("static/python/graph_global.html", auto_open=True)

################################ NUAGE DE MOTS

# Récupération des données de la colonne "FilteredWordsString"
cursor = collection.find({}, {'_id': 0, 'FilteredWordsString': 1})
data = list(cursor)

# Concaténation des mots en une seule chaîne de texte
text = ' '.join([entry['FilteredWordsString'] for entry in data])

# Création du nuage de mots
wordcloud = WordCloud(width=800, height=400).generate(text)

# Enregistrer le nuage de mots en tant qu'image
#wordcloud.to_file('static/python/wordcloud.png')

################################ TOP 10 RT

new_df_rt = df[["User_username", "Text", "Retweet Count"]]
new_df_rt = new_df_rt.sort_values("Retweet Count", ascending=False)
new_df_rt = new_df_rt.head(10)[["User_username", "Text", "Retweet Count"]]
#new_df_rt.to_html("static/python/tableRT.html", index=False)

################################ TOP 10 LIKES

new_df_lk = df[["User_username", "Text", "Like Count"]]
new_df_lk = new_df_lk.sort_values("Like Count", ascending=False)
new_df_lk = new_df_lk.head(10)[["User_username", "Text", "Like Count"]]
#new_df_lk.to_html("static/python/tableLIKES.html", index=False)

################################ TOP 10 QUOTES

new_df_qt = df[["User_username", "Text", "Quote Count"]]
new_df_qt = new_df_qt.sort_values("Quote Count", ascending=False)
new_df_qt = new_df_qt.head(10)[["User_username", "Text", "Quote Count"]]
#new_df_qt.to_html("static/python/tableQUOTES.html", index=False)

################################ TOP 10 USER

count_df = df['User_username'].value_counts().reset_index()
count_df.columns = ['User_username', 'Tweet']
top_10_users = count_df.head(10)
#top_10_users.to_html("static/python/tableUSER.html", index=False)

################################ GRAPH TWEET PAR MOIS

df['Mois'] = df['Datetime'].dt.month
df['Année'] = df['Datetime'].dt.year
grouped_df = df.groupby(['Mois', 'Année', 'sentiment_class']).size().reset_index(name='Count')
fig2 = px.bar(grouped_df, x='Mois', y='Count', color='sentiment_class', facet_col='Année', barmode='stack')
fig2.update_layout(
    title={
        'text': "Répartition des tweets par mois et année",
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white'}
    },
    xaxis_title='Mois',
    yaxis_title='Tweets',
    paper_bgcolor='rgba(22, 35, 49, 0.966)',
    plot_bgcolor='rgba(22, 35, 49, 0.966)',
    annotations=[{'font_color': 'white'}],
    xaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    yaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    legend=dict(
        title_font=dict(color='white'),
        title_font_color='white'
    )
)
fig2.write_html("static/python/graph_date.html")

################# GRAPH PAR JOUR
df['DayOfWeek'] = df['Datetime'].dt.day_name()
grouped_df = df['DayOfWeek'].value_counts().reset_index()
grouped_df.columns = ['DayOfWeek', 'Count']
fig3 = px.bar(grouped_df, x='DayOfWeek', y='Count', labels={'DayOfWeek': 'Jour de la semaine', 'Count': 'Tweets'})
fig3.update_layout(
    paper_bgcolor='rgba(22, 35, 49, 0.966)',
    plot_bgcolor='rgba(22, 35, 49, 0.966)',
    annotations=[{'font_color': 'white'}],
    xaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    yaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    legend=dict(
        title_font=dict(color='white'),
        title_font_color='white'
    )
)
fig3.write_html("static/python/graph_jour.html")

#############GRAPH PAR HEURE

df['Hour'] = df['Datetime'].dt.hour
grouped_df = df.groupby('Hour').size().reset_index(name='Count')
fig4 = px.scatter(grouped_df, x='Hour', y='Count', trendline='ols',
                 labels={'Hour': "Heure", 'Count': "Compte des lignes"})
fig4.update_layout(
    paper_bgcolor='rgba(22, 35, 49, 0.966)',
    plot_bgcolor='rgba(22, 35, 49, 0.966)',
    annotations=[{'font_color': 'white'}],
    xaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    yaxis=dict(
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    ),
    legend=dict(
        title_font=dict(color='white'),
        title_font_color='white'
    )
)
fig4.write_html("static/python/graph_heure.html")

################# TABLEAU JOURNEE IMPORTANTE


df['Date1'] = df['Datetime'].dt.date
df['Evenement'] = df['Date1'].astype(str)

filtered = ['2023-01-10', '2023-03-07', '2023-03-11', '2023-03-16', '2023-03-23', '2023-04-14']
df_filtered = df[df['Evenement'].isin(filtered)]

grouped_df = df_filtered.groupby(['Evenement', 'sentiment_class']).size().reset_index(name='Tweets')

#print(grouped_df)

fig5 = px.bar(grouped_df, x='Evenement', y='Tweets', color='sentiment_class', barmode='stack')
fig5.update_layout(
    title={
        'text': "Sentiments par évènement",
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white'}
    },
    paper_bgcolor='rgba(22, 35, 49, 0.966)',
    plot_bgcolor='rgba(22, 35, 49, 0.966)',
    font=dict(color='white')
)
fig5.write_html("static/python/graph_evenement.html", auto_open=True)