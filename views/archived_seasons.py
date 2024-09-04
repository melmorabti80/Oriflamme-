import streamlit as st
from db import load_archived_data, create_connection  # Ajout de create_connection
from game_logic import calculate_scores

def archived_seasons_view():
    st.title('Saisons archivées')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT SeasonID, SeasonName FROM seasons WHERE SeasonID IN (SELECT DISTINCT SeasonID FROM archived_games)")
        archived_seasons = cursor.fetchall()
        cursor.close()
        connection.close()

    if archived_seasons:
        selected_season_name = st.selectbox('Sélectionnez une Saison pour voir les détails', [season[1] for season in archived_seasons])
        selected_season_id = next(season[0] for season in archived_seasons if season[1] == selected_season_name)
        df = load_archived_data(selected_season_id)

        if not df.empty:
            st.header('Parties enregistrées de la saison archivée')
            st.table(df)
            
            st.header('Scores de la saison archivée')
            scores_df = calculate_scores(df)
            st.table(scores_df)
        else:
            st.write("Aucune partie enregistrée pour cette saison.")
    else:
        st.write("Aucune saison archivée disponible.")
