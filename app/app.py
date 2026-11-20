import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Catalogue", page_icon="🎬", layout="wide")

FICHIER = Path("catalogue/films.csv").parent.parent / "catalogue" / "films.csv"

@st.cache_data
def charger_donnees(chemin):
    return pd.read_csv(chemin)

df = charger_donnees(FICHIER)

st.title("Catalogue de films : l'explorateur")             # Titre
st.caption("Source : Bases IMDb et TMDB, données du 19/11/2026")                  # Légende sous le titre

with st.sidebar:                            # Barre latérale
    st.header("Filtres")
    note_moy_mini = st.slider("Note moyenne", 7.5, 10.0, 7.5, 0.1)                     # Curseur avec note moyenne minimale
    annee_min, annee_max = st.slider("Année de sortie", 1916, 2026, (1950, 2000), 1)           # Fourchette de prix avec curseur à deux poignées
    recherche = st.text_input("Titre")                                                 # Recherche dans les titres

st.subheader("Films sélectionnés")                                                     # Tableau listant les livres correspondant

selection = df.copy()                                                                  # Création d'une copie du fichier source

selection = selection[selection["note_moyenne"] >= note_moy_mini]                            # Filtre 1

selection = selection[selection["annee_sortie"] <= annee_max]                                # Filtre 2

selection = selection[selection["annee_sortie"] >= annee_min]                                # Filtre 3
if recherche:
    selection = selection[selection["titre_affiche"].str.contains(recherche, case=False)]

st.write("Films retenus :", len(selection), "sur", len(df))
st.dataframe(selection)

if len(selection) == 0:                                                                     # Message si aucun livre ne s'affiche
    st.warning("Aucun film ne correspond a ces criteres.")
else:
    gauche, milieu_gauche, milieu_droite, droite = st.columns(4)                            # 4 colonnes pour 4 KPIs

    gauche.metric("Nombre de films retenus", len(selection))                               # KPI 1

    milieu_gauche.metric("Le plus ancien", f"{selection['annee_sortie'].min()}")           # KPI 2

    milieu_droite.metric("Le plus récent", f"{selection['annee_sortie'].max()}")                             # KPI 3

    droite.metric("Note moyenne", f"{selection['note_moyenne'].mean():.2f} / 10")            # KPI 4

a, b = st.columns(2)
with a:                                                                                     # Tableau affichage des 5 mieux notés
    st.subheader("Les 5 mieux notés")
    st.dataframe(selection.nlargest(5, "note_moyenne")[["titre_affiche", "note_moyenne", "annee_sortie", "nombre_votes"]]) 

with b:                                                                                     # Tableau affichage des 5 - chers 
    st.subheader("Les 5 plus votés")
    st.dataframe(selection.nlargest(5, "nombre_votes")[["titre_affiche", "note_moyenne", "annee_sortie", "nombre_votes"]]) 
   

with st.expander("Voir les donnees brutes"):                                                # Affichage des données brutes
    st.dataframe(df)