"""
Grand Angle — Le ciné à la carte
Application Streamlit : choisir un film selon son émotion (6 salles = 6 émotions).

Lancement, depuis la racine du projet :
    streamlit run app/app.py
"""

from pathlib import Path
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors



# =============================================================================
# 1. CONFIGURATION
# =============================================================================

st.set_page_config(page_title="Grand Angle", page_icon="🎬", layout="wide")

# Chemin calculé depuis app.py : fonctionne quel que soit le dossier de lancement
FICHIER = Path(__file__).parent.parent / "catalogue" / "films.csv"

LOGO = Path(__file__).parent / "assets" / "logo_grand_angle.png"

# Les 6 salles du cinéma : une émotion = une salle
SALLES = {
    "rire":       {"salle": 1, "nom": "Comédies", "icone": "😂", "couleur": "#F5C518",
                   "accroche": "Les genres pour rire ensemble : Comédies, Animation et films familiaux."},
    "frissonner": {"salle": 2, "nom": "Frissons",       "icone": "😱", "couleur": "#8E44AD",
                   "accroche": "Les genres pour avoir le cœur qui bat : Thrillers, Polars et films d'horreur."},
    "emouvoir":   {"salle": 3, "nom": "Émotions",       "icone": "😢", "couleur": "#E84393",
                   "accroche": "Les genres pour fondre d'émotions : Romances, Drames et films musicaux."},
    "evader":     {"salle": 4, "nom": "Évasion",        "icone": "🚀", "couleur": "#00B894",
                   "accroche": "Les genres pour partir ailleurs : Aventure, Fantastique et Science-Fiction."},
    "reflechir":  {"salle": 5, "nom": "Réflexion",      "icone": "🧠", "couleur": "#0984E3",
                   "accroche": "Les genres pour comprendre le monde : Documentaires, Biographies et films historiques."},
    "vibrer":     {"salle": 6, "nom": "Adrénaline",     "icone": "🔥", "couleur": "#E72629",
                   "accroche": "Les genres pour faire monter la pression : Action, Guerre, Sport et Westerns."},
}

# Traduction des genres IMDb pour l'affichage
GENRES_FR = {
    "Action": "Action", "Adventure": "Aventure", "Animation": "Animation",
    "Biography": "Biographie", "Comedy": "Comédie", "Crime": "Policier",
    "Documentary": "Documentaire", "Drama": "Drame", "Family": "Famille",
    "Fantasy": "Fantastique", "Film-Noir": "Film noir", "History": "Histoire",
    "Horror": "Horreur", "Music": "Musique", "Musical": "Comédie musicale",
    "Mystery": "Mystère", "News": "Actualités", "Romance": "Romance",
    "Sci-Fi": "Science-fiction", "Sport": "Sport", "Thriller": "Thriller",
    "War": "Guerre", "Western": "Western",
}

AFFICHE_VIDE = "https://placehold.co/500x750/1f1f1f/777777?text=Affiche%0Aindisponible"


def html(code):
    """Affiche du HTML. Les lignes sont aplaties : sinon Markdown prend le HTML indenté pour du code."""
    st.markdown(" ".join(ligne.strip() for ligne in code.splitlines()), unsafe_allow_html=True)

# =============================================================================
# 2. STYLE « SALLE DE CINÉMA »
# =============================================================================

html(
    """
    <style>
    /* Fond sombre et police */
    .stApp { background-color: #0f0f0f; color: #f2f2f2; }
    [data-testid="stSidebar"] { background-color: #161616; }
    h1, h2, h3, h4 { color: #ffffff !important; }

    /* Boutons des émotions */
    .st-key-emotion_principale label p { font-size: 1.5rem !important; font-weight: 700; } 
    .st-key-emotion_principale button { padding: 0.9rem 1.3rem !important; }
    .st-key-emotion_principale button p { font-size: 1.1rem !important; }
    .st-key-recherche [data-testid="stWidgetLabel"] * { font-size: 1.7rem !important; font-weight: 700 !important; }

    /* Bandeau d'en-tête */
    .ga-logo { font-size: 2.4rem; font-weight: 900; letter-spacing: 0.08em; color: #E72629; margin: 0; }
    .ga-logo span { color: #ffffff; }
    .ga-tag { color: #9a9a9a; margin-top: -0.4rem; }

    /* Bannière de la salle */
    .ga-hero { border-radius: 14px; padding: 2rem 2.2rem; margin: 0.5rem 0 1.5rem 0;
               background: linear-gradient(90deg, rgba(0,0,0,0.92) 35%, rgba(0,0,0,0.35)), var(--fond);
               background-size: cover; background-position: center 25%; }
    .ga-salle { display: inline-block; padding: 0.25rem 0.8rem; border-radius: 6px;
                font-weight: 800; font-size: 0.9rem; color: #0f0f0f; background: var(--accent); }
    .ga-hero h2 { font-size: 2.6rem; margin: 0.6rem 0 0.3rem 0; }
    .ga-hero p { color: #d6d6d6; max-width: 640px; font-size: 1.05rem; }

    /* Titres de rangées */
    .ga-rangee { font-size: 2rem !important; font-weight: 700; margin: 1.6rem 0 0.6rem 0; color: #ffffff; }

    /* Cartes d'affiche */
    .ga-carte img { width: 100%; aspect-ratio: 2 / 3; object-fit: cover; border-radius: 8px;
                    transition: transform 0.25s ease, box-shadow 0.25s ease; }
    .ga-carte img:hover { transform: scale(1.05); box-shadow: 0 8px 24px rgba(0,0,0,0.7); }
    .ga-titre { font-weight: 700; font-size: 1.2rem; margin-top: 0.5rem; color: #ffffff;
                line-height: 1.3; min-height: 3.15;
                display: -webkit-box; -webkit-line-clamp:2; -webkit-box-orient: vertical; }
    .ga-meta { font-size: 0.95rem; color: #a0a0a0; }
    .ga-note { color: #F5C518; font-weight: 700; }

    /* Fiche film */
    .ga-fiche h2 { font-size: 2.4rem; margin-bottom: 0.2rem; }
    .ga-badge { display: inline-block; border: 1px solid #777; border-radius: 4px; padding: 0 0.45rem;
                margin-right: 0.4rem; font-size: 0.85rem; color: #d6d6d6; }
    .ga-label { color: #8a8a8a; }
    .ga-resume { font-size: 1.08rem; line-height: 1.6; color: #e6e6e6; }

    /* Boutons */
    .stButton > button { background-color: #262626; color: #ffffff; border: 1px solid #3a3a3a; }
    .stButton > button:hover { border-color: #E72629; color: #E72629; }
    </style>
    """
)

# =============================================================================
# 3. DONNÉES
# =============================================================================


@st.cache_data
def charger_donnees(chemin):
    df = pd.read_csv(chemin)
    C = df["note_moyenne"].mean()
    m = df["nombre_votes"].median()
    df["score"] = (df["nombre_votes"] / (df["nombre_votes"] + m)) * df["note_moyenne"] + (m / (df["nombre_votes"] + m)) * C
    df["affiche_url"] = df["affiche_url"].fillna(AFFICHE_VIDE)
    df["overview"] = df["overview"].fillna("Résumé indisponible.")
    # Le symbole $ déclenche l'affichage de formules mathématiques dans Streamlit : on l'échappe
    df["overview"] = df["overview"].str.replace("$", "\\$", regex=False)
    for col in ["acteurs", "realisateurs", "production_countries", "genres"]:
        df[col] = df[col].fillna("")
    return df

@st.cache_data
def listes_options(df):
    return {
        "genres": valeurs_uniques(df["genres"], ","),
        "realisateurs": valeurs_uniques(df["realisateurs"], ","),
        "acteurs": valeurs_uniques(df["acteurs"], ","),
        "pays": valeurs_uniques(df["production_countries"], ","),
    }

@st.cache_resource
def preparer_modele(df):
    genres_encodes = df["genres"].str.get_dummies(sep=",")                                  # Encodage des genres (catégoriels)
    langues_encodees = pd.get_dummies(df["original_language"], prefix="langue", dtype=int)  # Création d'une colonne encodée pour les langues originales
    scaler = StandardScaler().set_output(transform="pandas")                                # Standardisation des données 
    numeriques_scalees = scaler.fit_transform(df[["annee_sortie", "duree_min"]])            # Standardisation des années et des durée (numériques)
    X = pd.concat([numeriques_scalees, genres_encodes, langues_encodees], axis=1)           # Encodage des données numériques, des genres et des langues
    neighbors = NearestNeighbors(n_neighbors=51, metric="euclidean")                        # Instance du modèle
    neighbors.fit(X)                                                                        # Entraînement du modèle
    return X, neighbors                                                                     # Retour : X et le modèle


def valeurs_uniques(serie, separateur):
    """Liste triée des valeurs d'une colonne multi-valeurs (ex. 'Drama,Crime')."""
    valeurs = serie.str.split(separateur).explode().str.strip()
    return sorted(v for v in valeurs.dropna().unique() if v)


def contient_un_de(serie, choix, separateur):
    """Vrai si la case contient au moins une des valeurs choisies (comparaison exacte)."""
    choix = set(choix)
    return serie.str.split(separateur).apply(
        lambda liste: any(v.strip() in choix for v in liste) if isinstance(liste, list) else False
    )


def duree_lisible(minutes):
    return f"{int(minutes) // 60} h {int(minutes) % 60:02d}"


def genres_fr(genres):
    return ", ".join(GENRES_FR.get(g, g) for g in genres.split(",") if g)


df = charger_donnees(FICHIER)

if "film_choisi" not in st.session_state:
    st.session_state["film_choisi"] = None

options = listes_options(df)

X, neighbors = preparer_modele(df)

def recommander(tconst, emotion, emotion_2):
    position = df[df["tconst"] == tconst].index[0]                      # Position de la reco
    distances, indices = neighbors.kneighbors(X.iloc[[position]])       # Indices
    positions_voisins = indices[0][1:]                                  # on retire le film en position 0
    voisins = df.iloc[positions_voisins]                                # On affiche les reco
    voisins = voisins[voisins["poster_path"].notna()]          # On ne recommande que des films avec affiche
    voisins = voisins[voisins[f"emo_{emotion}"]]                        # Filtre sur les émotions 1 et 2
    if emotion_2:
        voisins = voisins[voisins[f"emo_{emotion_2}"]]
    return voisins.head(6)                                              # Retour : les 6 recos

# =============================================================================
# 4. EN-TÊTE ET CHOIX DE L'ÉMOTION (OBLIGATOIRE)
# =============================================================================

st.image(LOGO, width=230)
html('<p class="ga-tag">Le ciné à la carte · Paris 3e · 6 salles, 6 émotions</p>')


def libelle(cle):
    s = SALLES[cle]
    return f"{s['icone']} {s['nom']}"


emotion = st.segmented_control(
    "Quelle émotion vous tente ?",
    options=list(SALLES.keys()),
    format_func=libelle,
    selection_mode="single",
    default="rire",
    key="emotion_principale",
)

if emotion is None:
    st.info("Choisissez une émotion : elle vous indique votre salle.")
    st.stop()

salle = SALLES[emotion]

# =============================================================================
# 5. FILTRES (BARRE LATÉRALE)
# =============================================================================

with st.sidebar:
    st.markdown("## 🎟️ Affiner ma séance")

    autres = [c for c in SALLES if c != emotion]
    emotion_2 = st.pills(
        "Une 2e émotion ? (optionnel)",
        options=autres,
        format_func=libelle,
        selection_mode="single",
        key="emotion_secondaire",
    )

    annee_min, annee_max = st.slider(
        "📅 Années de sortie",
        int(df["annee_sortie"].min()), int(df["annee_sortie"].max()),
        (int(df["annee_sortie"].min()), int(df["annee_sortie"].max())),
    )

    note_min = st.slider("⭐ Note minimale", 7.5, 10.0, 7.5, 0.1)

    genres_choisis = st.multiselect(
        "🎭 Genres", options["genres"],
        format_func=lambda g: GENRES_FR.get(g, g), placeholder="Tous les genres",
    )
    realisateurs_choisis = st.multiselect(
        "🎬 Réalisateurs / réalisatrices", options["realisateurs"],
        placeholder="Tapez un nom…",
    )
    acteurs_choisis = st.multiselect(
        "🌟 Acteurs / actrices", options["acteurs"],
        placeholder="Tapez un nom…",
    )
    pays_choisis = st.multiselect(
        "🌍 Pays de production", options["pays"],
        placeholder="Tous les pays",
    )
    seulement_fr = st.toggle("🇫🇷 Films français uniquement")

# =============================================================================
# 6. APPLICATION DES FILTRES
# =============================================================================

selection = df[df[f"emo_{emotion}"]]
if emotion_2:
    selection = selection[selection[f"emo_{emotion_2}"]]

selection = selection[selection["annee_sortie"].between(annee_min, annee_max)]
selection = selection[selection["note_moyenne"] >= note_min]
selection = selection[selection["poster_path"].notna()]          # Pas de film sans affiche, ils restent trouvables par la recherche mais ne sont plus dans les rangées

if genres_choisis:
    selection = selection[contient_un_de(selection["genres"], genres_choisis, ",")]
if realisateurs_choisis:
    selection = selection[contient_un_de(selection["realisateurs"], realisateurs_choisis, ",")]
if acteurs_choisis:
    selection = selection[contient_un_de(selection["acteurs"], acteurs_choisis, ",")]
if pays_choisis:
    selection = selection[contient_un_de(selection["production_countries"], pays_choisis, ",")]
if seulement_fr:
    selection = selection[selection["film_francais"]]

# =============================================================================
# 7. COMPOSANTS D'AFFICHAGE
# =============================================================================


def rangee(titre, films, nb=6, cle=""):
    """Une rangée d'affiches façon plateforme, avec un bouton « Fiche » par film."""
    if films.empty:
        return
    html(f'<p class="ga-rangee">{titre}</p>')
    colonnes = st.columns(nb)
    for col, (_, film) in zip(colonnes, films.head(nb).iterrows()):
        with col:
            html(
                f"""
                <div class="ga-carte">
                    <img src="{film['affiche_url']}" alt="Affiche de {film['titre_affiche']}">
                    <div class="ga-titre">{film['titre_affiche']}</div>
                    <div class="ga-meta">{film['annee_sortie']} ·
                        <span class="ga-note">★ {film['note_moyenne']:.1f}</span></div>
                </div>
                """
            )
            if st.button("Voir la fiche", key=f"{cle}_{film['tconst']}", width="stretch"):
                st.session_state["film_choisi"] = film["tconst"]
                st.rerun()


def fiche(tconst):
    film = df[df["tconst"] == tconst].iloc[0]
    if st.button("← Retour à la salle"):
        st.session_state["film_choisi"] = None
        st.session_state["recherche"] = None    # vide la barre de recherche
        st.rerun()

    gauche, droite = st.columns([1, 2.2], gap="large")
    with gauche:
        html(f'<div class="ga-carte"><img src="{film["affiche_url"]}"></div>')
    with droite:
        badge_fr = '<span class="ga-badge">🇫🇷 Production française</span>' if film["film_francais"] else ""
        votes = f"{int(film['nombre_votes']):,}".replace(",", "\u202f")   # espace fine : 1 234 567
        html(
            f"""
            <div class="ga-fiche">
                <span class="ga-salle" style="--accent:{salle['couleur']}">
                    SALLE {salle['salle']} · {salle['nom'].upper()}</span>
                <h2>{film['titre_affiche']}</h2>
                <p class="ga-meta">{film['titre_international']}</p>
                <p>
                    <span class="ga-badge">{film['annee_sortie']}</span>
                    <span class="ga-badge">{duree_lisible(film['duree_min'])}</span>
                    <span class="ga-badge ga-note">★ {film['note_moyenne']:.1f} / 10</span>
                    <span class="ga-badge">{votes} votes</span>
                    {badge_fr}
                </p>
                <p class="ga-resume">{film['overview']}</p>
                <p><span class="ga-label">Réalisation : </span>{film['realisateurs'] or 'non renseigné'}</p>
                <p><span class="ga-label">Distribution : </span>{film['acteurs'] or 'non renseignée'}</p>
                <p><span class="ga-label">Genres : </span>{genres_fr(film['genres'])}</p>
                <p><span class="ga-label">Pays : </span>{film['production_countries'] or 'non renseigné'}</p>
            </div>
            """
        )

    recos = recommander(film["tconst"], emotion, emotion_2)
    if recos.empty:
        st.info("Aucun film de cette salle ne ressemble assez à ce titre. Essayez une autre émotion.")
    else:
        rangee("Si vous avez aimé ce film, vous aimerez…", recos, cle="similaires")

# =============================================================================
# 8. PAGE
# =============================================================================

if st.session_state["film_choisi"]:
    fiche(st.session_state["film_choisi"])
    st.stop()

# Bannière de la salle, illustrée par l'affiche du film le mieux noté de la sélection
vedette = selection.sort_values(["score", "nombre_votes"], ascending=False).head(1)
fond = f"url('{vedette['affiche_url'].iloc[0]}')" if not vedette.empty else "none"
sous_titre = f" · avec {libelle(emotion_2)}" if emotion_2 else ""

html(
    f"""
    <div class="ga-hero" style="--fond:{fond}; --accent:{salle['couleur']}">
        <span class="ga-salle">SALLE {salle['salle']}</span>
        <h2>{salle['icone']} {salle['nom']}{sous_titre}</h2>
        <p>{salle['accroche']}</p>
        <p><b>{len(selection)}</b> films à l'affiche pour vous.</p>
    </div>
    """
)

if selection.empty:
    st.warning("Aucun film ne correspond à ces critères. Essayez d'élargir vos filtres.")
    st.stop()

# Recherche directe d'un film
choix = st.selectbox(
    "🔎 Vous avez un film en tête ?",
    options=df["tconst"],
    format_func=lambda t: f"{df.loc[df['tconst'] == t, 'titre_affiche'].iloc[0]} "
                         f"({df.loc[df['tconst'] == t, 'annee_sortie'].iloc[0]})",
    index=None,
    placeholder="Tapez un titre…",
    key="recherche",
)
if choix:
    st.session_state["film_choisi"] = choix
    st.rerun()

# Rangées thématiques
rangee("⭐ Les mieux notés de la salle",
       selection.sort_values(["score", "nombre_votes"], ascending=False), cle="top")
rangee("🔥 Les plus populaires",
       selection.sort_values("nombre_votes", ascending=False), cle="pop")
rangee("🆕 Sortis depuis 2015",
       selection[selection["annee_sortie"] >= 2015].sort_values("score", ascending=False), cle="recents")
rangee("🎞️ Les grands classiques (avant 1970)",
       selection[selection["annee_sortie"] < 1970].sort_values("score", ascending=False), cle="classiques")
rangee("Le cinéma français",
       selection[selection["film_francais"]].sort_values("score", ascending=False), cle="fr")
rangee("💎 Pépites méconnues (moins de 7 500 votes)",
       selection[selection["nombre_votes"] < 7500].sort_values("note_moyenne", ascending=False), cle="pepites")


st.caption("Sources : IMDb et TMDB · données du 19/11/2026 · Grand Angle, Groupe 3")