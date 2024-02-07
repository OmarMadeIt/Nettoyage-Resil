import streamlit as st
import pandas as pd
from datetime import datetime


def clean_dataframe(df):
    # Supprimer les lignes contenant '-----' dans la colonne 'CGEST'
    df = df[df['CGEST'] != '-----']
    df = df.rename(columns=lambda x: x.strip())
        
        # Supprimer les espaces des valeurs dans les colonnes de dates
    df['DATE_RS'] = df['DATE_RS'].str.strip()
    for colonne in df.columns:
        df[colonne] = df[colonne].str.strip()
    # Supprimer les lignes avec des valeurs vides ou espaces dans les colonnes de dates
    df = df[df['DATE_RS'].str.len() > 0]

    # Convertir les colonnes de dates au format dd/mm/yyyy
    #date_columns = ['DATDEB_F', 'DATE_RS']
    date_columns = ['DATE_RS']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%y').dt.strftime('%d/%m/%Y')

    return df

# Partie Streamlit
st.title("Nettoyage de fichier TXT")

uploaded_file = st.file_uploader("Uploader le fichier txt", type=['txt'])

if uploaded_file is not None:
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(uploaded_file, sep='|', encoding='latin-1')
        st.write("La taille du fichier chargé: ", df['ND             '].count())
        # Nettoyage du DataFrame
        df = clean_dataframe(df)
        st.write("La taille du fichier Nettoyé: ", df['ND'].count())
        st.write(df[df['ND']==338212143])
        # Affichage des premières lignes du DataFrame nettoyé
        st.write("Aperçu des données nettoyées :")
        st.write(df.head())

        st.write("DataFrame complet :")
        st.write(df)

    except Exception as e:
        st.error("Une erreur s'est produite lors de la lecture du fichier : {}".format(str(e)))
        
# ---- SIDEBAR ----

st.sidebar.header("Filtrez les éléments ici :")
acces_reseau = st.sidebar.multiselect(
    "Selectionner l'offre:",
    options=df['ACCES_RESEAU'].unique(),
    default=df['ACCES_RESEAU'].unique()[0]
)

motif = st.sidebar.multiselect(
    "Selectionner l'offre:",
    options=df['MOTIF'].unique(),
    default=df['MOTIF'].unique()[0]
    
)


# Filtrer sur les colonnes de dates
start_date = st.date_input("Date de début", value=None)
end_date = st.date_input("Date de fin", value=None)


if st.button('Soumettre'):
    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()

        df_selection = df.query(
            "ACCES_RESEAU == @acces_reseau & MOTIF == @motif"
        )
        df_selection['DATE_RS'] = pd.to_datetime(df_selection['DATE_RS'], format='%d/%m/%Y')

    if start_date is not None and end_date is not None:
        df_selection = df_selection[
            (pd.to_datetime(df_selection['DATE_RS']).dt.date >= start_date)
            & (pd.to_datetime(df_selection['DATE_RS']).dt.date <= end_date)
        ]

    st.title("Affichage de la base filtrée")
    st.write(df_selection.groupby(['ACCES_RESEAU', 'MOTIF'])['ND'].count().reset_index())
    st.write(df_selection)
    st.write("La base contient : ", df_selection['ND'].count())
            # Bouton pour exporter le DataFrame en CSV
    st.download_button(
       "Télécharger le fichier",
       df_selection.to_csv(index=False, sep=';'),
       "file.csv",
       "text/csv",
       key='download-csv'
    )
