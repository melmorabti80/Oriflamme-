import streamlit as st
from streamlit_option_menu import option_menu
from views.current_season import current_season_view
from views.archived_seasons import archived_seasons_view
from db import create_database, verify_and_create_tables, ensure_current_season

# Créer la base de données si elle n'existe pas
create_database()

# Vérifier et créer les tables si nécessaire
verify_and_create_tables()

# Assurer qu'une saison actuelle existe
ensure_current_season()

# Interface utilisateur avec menu latéral et icônes
with st.sidebar:
    menu = option_menu(
        "Menu de Navigation",
        ["Saison en cours", "Saisons archivées"],
        icons=["calendar", "archive"],  # Icônes correspondantes (utilise la librairie Bootstrap Icons)
        menu_icon="cast",  # Icône du menu principal
        default_index=0,  # L'option par défaut est "Saison en cours"
    )

# Affichage des vues en fonction du menu sélectionné
if menu == "Saison en cours":
    current_season_view()
elif menu == "Saisons archivées":
    archived_seasons_view()
