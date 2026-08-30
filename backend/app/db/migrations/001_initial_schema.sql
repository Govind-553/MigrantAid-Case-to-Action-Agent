-- Migration: 001_initial_schema.sql
-- Description: Create initial tables for MigrantAid case persistence

CREATE TABLE IF NOT EXISTS cases (
    id VARCHAR(128) PRIMARY KEY,
    narrative TEXT NOT NULL,
    status VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS case_facts (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    field VARCHAR(128) NOT NULL,
    value JSONB NOT NULL,
    status VARCHAR(64) NOT NULL,
    source VARCHAR(256) NOT NULL DEFAULT 'user_input',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS case_needs (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    category VARCHAR(128) NOT NULL,
    priority VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL,
    evidence_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resource_recommendations (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    resource_id VARCHAR(128) NOT NULL,
    resource_name VARCHAR(256) NOT NULL DEFAULT '',
    need_category VARCHAR(128),
    retrieval_score DOUBLE PRECISION,
    status VARCHAR(64) NOT NULL,
    source_id VARCHAR(128) NOT NULL,
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_results (
    id BIGSERIAL PRIMARY KEY,
    recommendation_id BIGINT NOT NULL REFERENCES resource_recommendations(id) ON DELETE CASCADE,
    requirement_id VARCHAR(128) NOT NULL,
    field VARCHAR(128) NOT NULL,
    status VARCHAR(64) NOT NULL,
    evidence_text TEXT,
    case_fact_value JSONB,
    required_value JSONB,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS action_plan_items (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    step INT NOT NULL,
    priority VARCHAR(64) NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    prerequisite TEXT,
    responsible_role TEXT,
    evidence_reference TEXT,
    unresolved_uncertainty TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS human_reviews (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL UNIQUE REFERENCES cases(id) ON DELETE CASCADE,
    decision VARCHAR(64) NOT NULL,
    reviewer_notes TEXT,
    reviewed_at TIMESTAMPTZ,
    modified_recommendation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    rejected_recommendation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    follow_up_required BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trajectory_events (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    stage VARCHAR(128) NOT NULL,
    agent VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    tool_call TEXT,
    tool_response_summary TEXT,
    verification_result TEXT,
    error_message TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    latency_ms DOUBLE PRECISION,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_case_facts_case_id ON case_facts(case_id);
CREATE INDEX IF NOT EXISTS idx_case_needs_case_id ON case_needs(case_id);
CREATE INDEX IF NOT EXISTS idx_resource_recommendations_case_id ON resource_recommendations(case_id);
CREATE INDEX IF NOT EXISTS idx_verification_results_rec_id ON verification_results(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_action_plan_items_case_id ON action_plan_items(case_id);
CREATE INDEX IF NOT EXISTS idx_human_reviews_case_id ON human_reviews(case_id);
CREATE INDEX IF NOT EXISTS idx_trajectory_events_case_id ON trajectory_events(case_id);
