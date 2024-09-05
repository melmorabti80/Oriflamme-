import streamlit as st
from streamlit_option_menu import option_menu
from views.current_season import current_season_view
from views.archived_seasons import archived_seasons_view
from views.delete_data import delete_data_view
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
        ["Saison en cours", "Saisons archivées", "Suppression de données"],
        icons=["calendar", "archive", "trash"],  
        menu_icon="cast",
        default_index=0,
    )

# Affichage des vues en fonction du menu sélectionné
if menu == "Saison en cours":
    current_season_view()
elif menu == "Saisons archivées":
    archived_seasons_view()
elif menu == "Suppression de données":
    delete_data_view()
