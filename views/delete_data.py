import streamlit as st
from db import create_connection, delete_season, delete_all_archived_seasons

def delete_data_view():
    st.title("Suppression de données")

    # Option pour supprimer une saison en particulier
    connection = create_connection()
    seasons = []
    if connection:
        cursor = connection.cursor()
        # Sélectionner uniquement les saisons qui ont encore des parties associées
        cursor.execute("""
            SELECT s.SeasonID, s.SeasonName
            FROM seasons s
            LEFT JOIN games g ON s.SeasonID = g.SeasonID
            LEFT JOIN archived_games ag ON s.SeasonID = ag.SeasonID
            WHERE g.SeasonID IS NOT NULL OR ag.SeasonID IS NOT NULL
        """)
        seasons = cursor.fetchall()
        cursor.close()
        connection.close()

    if seasons:
        st.subheader("Supprimer une saison en particulier")
        selected_season = st.selectbox('Sélectionnez une Saison', [season[1] for season in seasons])

        if st.button("Supprimer la saison sélectionnée"):
            selected_season_id = next(season[0] for season in seasons if season[1] == selected_season)
            delete_season(selected_season_id)
            st.success(f"La saison {selected_season} et toutes ses parties ont été supprimées.")
    
    # Option pour supprimer toutes les saisons archivées
    st.subheader("Supprimer toutes les saisons archivées")
    if st.button("Supprimer toutes les saisons archivées"):
        delete_all_archived_seasons()
        st.success("Toutes les saisons archivées et leurs parties ont été supprimées.")
