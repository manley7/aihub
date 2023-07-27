"""Added cluster tables

Revision ID: a97ba61bc99c
Revises: 5184645e9f12
Create Date: 2023-07-26 09:04:56.494099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a97ba61bc99c'
down_revision = '5184645e9f12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cluster_agents',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cluster_id', sa.Integer(), nullable=True),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cluster_configurations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cluster_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(), nullable=True),
    sa.Column('value', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cluster_executions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('cluster_id', sa.Integer(), nullable=True),
    sa.Column('last_execution_time', sa.DateTime(), nullable=True),
    sa.Column('num_of_calls', sa.Integer(), nullable=True),
    sa.Column('num_of_tokens', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clusters',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('ix_agent_schedule_agent_id', table_name='agent_schedule')
    op.drop_index('ix_agent_schedule_expiry_date', table_name='agent_schedule')
    op.drop_index('ix_agent_schedule_status', table_name='agent_schedule')
    op.alter_column('agent_workflow_steps', 'unique_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('agent_workflow_steps', 'step_type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('agent_workflows', 'organisation_id')
    op.drop_index('ix_events_agent_id', table_name='events')
    op.drop_index('ix_events_event_property', table_name='events')
    op.drop_index('ix_events_org_id', table_name='events')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_events_org_id', 'events', ['org_id'], unique=False)
    op.create_index('ix_events_event_property', 'events', ['event_property'], unique=False)
    op.create_index('ix_events_agent_id', 'events', ['agent_id'], unique=False)
    op.add_column('agent_workflows', sa.Column('organisation_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.alter_column('agent_workflow_steps', 'step_type',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('agent_workflow_steps', 'unique_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_index('ix_agent_schedule_status', 'agent_schedule', ['status'], unique=False)
    op.create_index('ix_agent_schedule_expiry_date', 'agent_schedule', ['expiry_date'], unique=False)
    op.create_index('ix_agent_schedule_agent_id', 'agent_schedule', ['agent_id'], unique=False)
    op.drop_table('clusters')
    op.drop_table('cluster_executions')
    op.drop_table('cluster_configurations')
    op.drop_table('cluster_agents')
    # ### end Alembic commands ###
