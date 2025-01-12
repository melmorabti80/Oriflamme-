import streamlit as st
from db import load_archived_data, create_connection, delete_game  # Ajout des imports nécessaires
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

            # Bouton pour restaurer la saison archivée
            if st.button('Restaurer cette saison comme saison en cours'):
                restore_archived_season(selected_season_id)
                st.success(f'La saison "{selected_season_name}" a été restaurée comme saison en cours ! Les données de la saison précédente ont été supprimées.')
        else:
            st.write("Aucune partie enregistrée pour cette saison.")
    else:
        st.write("Aucune saison archivée disponible.")


def restore_archived_season(season_id):
    """
    Restaure une saison archivée comme saison en cours.
    Supprime également les données de la saison en cours actuelle.
    """
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Récupérer la saison actuelle
            cursor.execute("SELECT SeasonID FROM seasons ORDER BY SeasonID DESC LIMIT 1")
            current_season = cursor.fetchone()
            if current_season:
                current_season_id = current_season[0]

                # Supprimer les parties de la saison actuelle
                cursor.execute("DELETE FROM games WHERE SeasonID = %s", (current_season_id,))

                # Supprimer la saison actuelle
                cursor.execute("DELETE FROM seasons WHERE SeasonID = %s", (current_season_id,))

            # Restaurer les parties de la saison archivée dans la table `games`
            cursor.execute("""
                INSERT INTO games (Winning_Team, Losing_Team, DatePlayed, SeasonID)
                SELECT Winning_Team, Losing_Team, DatePlayed, SeasonID
                FROM archived_games
                WHERE SeasonID = %s
            """, (season_id,))

            # Supprimer les parties restaurées de la table `archived_games`
            cursor.execute("DELETE FROM archived_games WHERE SeasonID = %s", (season_id,))

            connection.commit()
        except Error as e:
            st.error(f"Erreur lors de la restauration de la saison : {e}")
        finally:
            cursor.close()
            connection.close()
