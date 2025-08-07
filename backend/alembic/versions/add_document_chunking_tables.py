"""Add document chunking tables for large PDF processing

Revision ID: add_document_chunking
Revises: add_custom_fields_table
Create Date: 2025-08-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'add_document_chunking'
down_revision = 'add_custom_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_number', sa.Integer(), nullable=False),
        sa.Column('start_page', sa.Integer(), nullable=False),
        sa.Column('end_page', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('extraction_method', sa.String(), nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('extracted_fields', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('file_size_mb', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('api_calls_made', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_retry_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_status'), 'document_chunks', ['status'], unique=False)
    
    # Create processing_logs table
    op.create_table(
        'processing_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('extraction_method', sa.String(), nullable=True),
        sa.Column('log_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processing_logs_document_id'), 'processing_logs', ['document_id'], unique=False)
    op.create_index(op.f('ix_processing_logs_chunk_id'), 'processing_logs', ['chunk_id'], unique=False)
    op.create_index(op.f('ix_processing_logs_created_at'), 'processing_logs', ['created_at'], unique=False)
    
    # Create processing_metrics table
    op.create_table(
        'processing_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('total_pages', sa.Integer(), nullable=False),
        sa.Column('total_chunks', sa.Integer(), nullable=False),
        sa.Column('processed_pages', sa.Integer(), nullable=True),
        sa.Column('completed_chunks', sa.Integer(), nullable=True),
        sa.Column('failed_chunks', sa.Integer(), nullable=True),
        sa.Column('landing_ai_api_count', sa.Integer(), nullable=True),
        sa.Column('landing_ai_sdk_count', sa.Integer(), nullable=True),
        sa.Column('openai_fallback_count', sa.Integer(), nullable=True),
        sa.Column('avg_chunk_time_ms', sa.Float(), nullable=True),
        sa.Column('total_processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('total_api_calls', sa.Integer(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=True),
        sa.Column('has_failures', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('actual_completion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    
    # Add new columns to documents table
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_chunked', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('total_chunks', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('completed_chunks', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('file_size_mb', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('page_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('chunk_size', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('processing_strategy', sa.String(), nullable=True))
    
    # Set defaults for existing documents
    op.execute("UPDATE documents SET is_chunked = 0 WHERE is_chunked IS NULL")
    op.execute("UPDATE documents SET total_chunks = 0 WHERE total_chunks IS NULL")
    op.execute("UPDATE documents SET completed_chunks = 0 WHERE completed_chunks IS NULL")
    op.execute("UPDATE documents SET chunk_size = 40 WHERE chunk_size IS NULL")
    op.execute("UPDATE documents SET processing_strategy = 'SEQUENTIAL' WHERE processing_strategy IS NULL")

def downgrade():
    # Drop new columns from documents table
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('processing_strategy')
        batch_op.drop_column('chunk_size')
        batch_op.drop_column('page_count')
        batch_op.drop_column('file_size_mb')
        batch_op.drop_column('completed_chunks')
        batch_op.drop_column('total_chunks')
        batch_op.drop_column('is_chunked')
    
    # Drop tables
    op.drop_table('processing_metrics')
    op.drop_index(op.f('ix_processing_logs_created_at'), table_name='processing_logs')
    op.drop_index(op.f('ix_processing_logs_chunk_id'), table_name='processing_logs')
    op.drop_index(op.f('ix_processing_logs_document_id'), table_name='processing_logs')
    op.drop_table('processing_logs')
    op.drop_index(op.f('ix_document_chunks_status'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
    op.drop_table('document_chunks')