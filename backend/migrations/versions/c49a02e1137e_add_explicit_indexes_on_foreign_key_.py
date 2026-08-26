"""add explicit indexes on foreign key columns

Revision ID: c49a02e1137e
Revises: c38af627e0ef
Create Date: 2026-08-26 11:43:29.647236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c49a02e1137e'
down_revision = 'c38af627e0ef'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_tournaments_organizer_id', 'tournaments', ['organizer_id'])
    op.create_index('ix_players_team_id', 'players', ['team_id'])
    op.create_index('ix_players_user_id', 'players', ['user_id'])
    op.create_index('ix_participants_player_id', 'participants', ['player_id'])
    op.create_index('ix_participants_team_id', 'participants', ['team_id'])
    op.create_index('ix_tournament_participants_tournament_id', 'tournament_participants', ['tournament_id'])
    op.create_index('ix_tournament_participants_participant_id', 'tournament_participants', ['participant_id'])
    op.create_index('ix_matches_tournament_id', 'matches', ['tournament_id'])
    op.create_index('ix_matches_venue_id', 'matches', ['venue_id'])
    op.create_index('ix_match_participants_match_id', 'match_participants', ['match_id'])
    op.create_index('ix_match_participants_participant_id', 'match_participants', ['participant_id'])
    op.create_index('ix_match_results_match_id', 'match_results', ['match_id'])
    op.create_index('ix_match_results_winner_participant_id', 'match_results', ['winner_participant_id'])
    op.create_index('ix_standings_tournament_id', 'standings', ['tournament_id'])
    op.create_index('ix_standings_participant_id', 'standings', ['participant_id'])


def downgrade():
    op.drop_index('ix_standings_participant_id', table_name='standings')
    op.drop_index('ix_standings_tournament_id', table_name='standings')
    op.drop_index('ix_match_results_winner_participant_id', table_name='match_results')
    op.drop_index('ix_match_results_match_id', table_name='match_results')
    op.drop_index('ix_match_participants_participant_id', table_name='match_participants')
    op.drop_index('ix_match_participants_match_id', table_name='match_participants')
    op.drop_index('ix_matches_venue_id', table_name='matches')
    op.drop_index('ix_matches_tournament_id', table_name='matches')
    op.drop_index('ix_tournament_participants_participant_id', table_name='tournament_participants')
    op.drop_index('ix_tournament_participants_tournament_id', table_name='tournament_participants')
    op.drop_index('ix_participants_team_id', table_name='participants')
    op.drop_index('ix_participants_player_id', table_name='participants')
    op.drop_index('ix_players_user_id', table_name='players')
    op.drop_index('ix_players_team_id', table_name='players')
    op.drop_index('ix_tournaments_organizer_id', table_name='tournaments')
