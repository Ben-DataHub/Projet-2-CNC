🎬 Projet 2 — Cinéma CNC & moteur de recommandation

Réponse à l'appel à projets du CNC : un cinéma à Paris, au catalogue large et varié, pensé pour choisir un film selon l'émotion recherchée (rire, frissonner, réfléchir, s'évader…), avec une application de recommandation de films.

Équipe : [Prénom 1], [Prénom 2], [Prénom 3], Benjamin
Soutenance : lundi 7 décembre 2026

📁 Structure du dépôt
Projet-2-CNC/
├── data/                  # Données locales (NON versionnées, voir .gitignore)
├── notebooks/
│   └── analyse_data.ipynb # Préparation des données : fichiers bruts → catalogue
├── app/                   # Application Streamlit (à venir)
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
🗂️ Données

Les données ne sont pas dans le dépôt (trop volumineuses).

Source	Fichiers	Comment les obtenir
IMDb	title.basics, title.ratings, title.akas	Lus directement en ligne depuis datasets.imdbws.com : rien à télécharger
TMDB	TMDB_movie_dataset_v11.csv	Lien Drive fourni sur Simplonline → à placer dans data/

⚠️ Créer le dossier data/ à la racine du projet s'il n'existe pas, puis y déposer le fichier TMDB.

🧹 Préparation des données

Notebook : notebooks/analyse_data.ipynb. Le lancer de haut en bas (Restart → Run All).

Règles de filtrage du catalogue
Filtre	Règle	Justification
Type	titleType == "movie"	Uniquement des films de cinéma (exclut séries, épisodes, courts métrages)
Contenu adulte	isAdult == 0	Cinéma tout public
Année	startYear >= 1920	Des classiques aux films récents
Notoriété	numVotes >= 5 000	Films reconnus par le public
Qualité	averageRating >= 7.5	Films bien notés

Résultat : [X] films au départ → [X] films dans le catalogue final.

Titres français
Source : title.akas, filtré sur region == "FR" (et non language == "fr", qui renvoie surtout des titres québécois).
Films sans titre FR : on garde le titre d'origine (primaryTitle).
Films français

[Méthode retenue avec TMDB + sa limite : à compléter]

🎯 Recommandation

[Colonnes utilisées, méthode, justification : à compléter]

🚀 Lancer l'application
bash
streamlit run app/app.py

L'application s'ouvre dans le navigateur (par défaut : http://localhost:8501).

[Adapter le chemin si le fichier de l'app change de nom]

🛠️ Outils

Python · pandas · scikit-learn · Streamlit · [Power BI / Looker Studio / Tableau] · GitHub