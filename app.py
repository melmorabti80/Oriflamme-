import streamlit as st
from views.current_season import current_season_view
from views.archived_seasons import archived_seasons_view
from db import create_database, verify_and_create_tables, ensure_current_season

# Créer la base de données si elle n'existe pas
create_database()

# Vérifier et créer les tables si nécessaire
verify_and_create_tables()

# Assurer qu'une saison actuelle existe
ensure_current_season()

# Interface utilisateur avec menu latéral
st.sidebar.title("Menu de Navigation")
menu = st.sidebar.radio("Choisissez une option", ["Saison en cours", "Saisons archivées"])

if menu == "Saison en cours":
    current_season_view()
elif menu == "Saisons archivées":
    archived_seasons_view()
