🎬 Grand Angle — Le ciné à la carte

Réponse du Groupe 3 à l'appel à projets du CNC : un cinéma tous publics au cœur du 3e arrondissement de Paris (le Marais), qui remet à l'affiche les grands classiques de toutes les époques et des films très bien notés, en séances spéciales, cycles et ciné-clubs, avec une application de recommandation de films.

Équipe : Mariame, Hélène, Benjamin P., Benjamin F.
Soutenance : lundi 7 décembre 2026

📁 Structure du dépôt
Projet-2-CNC/
├── catalogue/
│   └── films.csv          # Catalogue final (3 323 films), partagé avec le groupe
├── data/                  # Données brutes locales (NON versionnées, voir .gitignore)
├── notebooks/
│   └── analyse_data.ipynb # Préparation des données : fichiers bruts → catalogue
├── app/                   # Application Streamlit (en cours)
├── requirements.txt       # Dépendances Python
└── README.md
⚙️ Installation
1. Cloner le dépôt
bash
git clone https://github.com/Ben-DataHub/Projet-2-CNC.git
cd Projet-2-CNC
2. Créer et activer un environnement virtuel
bash
python -m venv .venv
Windows (Git Bash) : source .venv/Scripts/activate
Windows (PowerShell) : .venv\Scripts\Activate.ps1
Mac / Linux : source .venv/bin/activate
3. Installer les dépendances
bash
pip install -r requirements.txt
🗂️ Données sources
Source	Fichiers	Comment les obtenir
IMDb	title.basics, title.ratings, title.akas, title.principals, name.basics	Lus directement en ligne depuis datasets.imdbws.com : rien à télécharger
TMDB	TMDB_movie_dataset_v11.csv	Lien Drive fourni sur Simplonline → à placer dans data/

⚠️ Créer le dossier data/ à la racine du projet s'il n'existe pas, puis y déposer le fichier TMDB. Le catalogue final (catalogue/films.csv) est déjà dans le dépôt : pas besoin de relancer le notebook pour utiliser l'application.

🧹 Préparation des données

Notebook : notebooks/analyse_data.ipynb. Le lancer de haut en bas (Restart → Run All). Les gros fichiers IMDb (akas, principals, name.basics) sont lus par morceaux (chunksize) : compter plusieurs minutes.

Entonnoir de filtrage
Étape	Règle	Films restants
Point de départ	Titres IMDb notés (basics × ratings)	1 734 008
Type	titleType == "movie" : longs métrages uniquement	352 019
Notoriété	numVotes >= 5 000 : assez de votes pour une note fiable	19 291
Qualité	averageRating >= 7.5 : films très bien notés	3 323
Tout public	isAdult == 0	3 323

Pas de filtre d'année ni de durée : le catalogue couvre toutes les époques (de 1916 à 2026).

Titres français
Source : title.akas, filtré sur region == "FR", et non language == "fr", qui renvoie surtout des titres québécois.
2 705 films (≈ 81 %) ont un titre France. Les autres gardent leur titre international (primaryTitle).
Contrôle : tt0111161 → Les Évadés (et non À l'ombre de Shawshank, le titre québécois).
Enrichissement TMDB
Jointure tconst (IMDb) = imdb_id (TMDB), en left join : aucun film du catalogue n'est perdu.
Doublons TMDB : pour un même film, on garde la ligne avec le plus de votes (vote_count).
143 films sans affiche (absents de TMDB, ou présents sans affiche).
Films français
Règle : la France figure parmi les pays de production (production_countries contient « France »).
397 films (11,9 %).
⚠️ Limite : les coproductions comptent. Un film étranger coproduit avec la France est compté comme français.
Distribution
Source : title.principals + name.basics.
Les 3 premiers acteurs ou actrices au générique (ordering), et le ou les réalisateurs.
Contrôles qualité
Lecture : séparateur tabulation, \N converti en valeur manquante, types numériques corrigés (to_numeric, puis Int64).
0 valeur manquante sur l'année et la durée.
0 doublon : une ligne par film.
Valeurs cohérentes : notes de 7,5 à 9,8, de 5 000 à 3,3 M de votes, durées de 45 à 566 min.
📋 Dictionnaire du catalogue (catalogue/films.csv)
Colonne	Description
tconst	Identifiant IMDb du film (clé unique)
titre_international	Titre le plus courant sur IMDb (souvent anglais)
titre_affiche	Titre affiché au public : titre France s'il existe, sinon titre international
annee_sortie	Année de sortie
duree_min	Durée en minutes
genres	Jusqu'à 3 genres, séparés par une virgule
note_moyenne	Note moyenne IMDb (sur 10)
nombre_votes	Nombre de votes IMDb
original_language	Langue d'origine (TMDB)
production_countries	Pays de production, en anglais (TMDB)
production_companies	Sociétés de production (TMDB)
overview	Résumé du film (TMDB)
poster_path	Fin du chemin de l'affiche (TMDB)
affiche_url	Adresse complète de l'affiche (500 px)
film_francais	True si la France figure parmi les pays de production
acteurs	Les 3 premiers acteurs ou actrices au générique
realisateurs	Réalisateur(s)

💡 Import dans Power BI : choisir les paramètres régionaux Anglais (États-Unis), car les décimales sont écrites avec un point.

🎯 Recommandation

Notebook : notebooks/recommandation_ML.ipynb · intégrée dans app/app2.py (fonction films_similaires)

Principe : quand le spectateur ouvre la fiche d'un film qu'il aime, l'application lui propose des films proches, dans la salle de l'émotion choisie.

Colonnes utilisées (features)
- genres : transformés en 23 colonnes 0/1 (get_dummies)
- note_moyenne, annee_sortie, duree_min : ramenées entre 0 et 1 (MinMaxScaler), pour qu'aucune ne pèse plus que les autres
→ matrice X de 3 323 films × 26 colonnes

Méthode
- Modèle non supervisé : NearestNeighbors (scikit-learn), distance euclidienne
- On cherche les 20 films les plus proches du film aimé, parmi ceux de l'émotion choisie
- On en tire 6 au hasard : des propositions pertinentes, mais qui varient à chaque visite

Pourquoi ce choix
- Aucune donnée client (démarrage à froid) : on se base uniquement sur les caractéristiques des films
- Pas de « bonne réponse » à prédire : le non supervisé est adapté

Essai supervisé
- KNeighborsClassifier (80 % entraînement / 20 % test) pour prédire les émotions : score de 0,95
- Score trop beau : les colonnes emo_ sont déduites des genres, donc le modèle connaissait déjà la réponse (fuite de données). On a gardé l'approche non supervisée.

Pistes d'amélioration
- Ajouter les réalisateurs et les acteurs aux features

🚀 Lancer l'application
bash
streamlit run app/app.py

L'application s'ouvre dans le navigateur (par défaut : http://localhost:8501).

🛠️ Outils

Python · pandas · scikit-learn · Streamlit · Power BI · GitHub