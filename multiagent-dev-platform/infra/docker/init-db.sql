-- Initialize multiagent platform database
-- This script creates the necessary tables for journal, audit, and mission tracking

-- Missions table: tracks all development missions
CREATE TABLE IF NOT EXISTS missions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_by VARCHAR(100),
    plan JSONB,
    mission_metadata JSONB
);

-- Tasks table: individual tasks within missions
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    mission_id INTEGER REFERENCES missions(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB,
    error TEXT,
    task_metadata JSONB
);

-- Agent executions: detailed log of agent actions
CREATE TABLE IF NOT EXISTS agent_executions (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    input JSONB,
    output JSONB,
    success BOOLEAN DEFAULT true,
    error TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- External AI calls: audit trail of external AI usage
CREATE TABLE IF NOT EXISTS external_ai_calls (
    id SERIAL PRIMARY KEY,
    mission_id INTEGER REFERENCES missions(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    purpose TEXT NOT NULL,
    justification TEXT NOT NULL,
    approved BOOLEAN DEFAULT false,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    request JSONB,
    response JSONB,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    cached BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory items: approved content for RAG
CREATE TABLE IF NOT EXISTS memory_items (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL, -- adr, playbook, snippet, glossary
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    vector_id VARCHAR(100), -- Reference to Qdrant vector
    approved BOOLEAN DEFAULT false,
    approved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    item_metadata JSONB
);

-- Validation results: lint, test, build results
CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    mission_id INTEGER REFERENCES missions(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL, -- lint, test, build
    success BOOLEAN NOT NULL,
    output TEXT,
    errors JSONB,
    warnings JSONB,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_created_at ON missions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_mission_id ON tasks(mission_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_task_id ON agent_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_external_ai_calls_mission_id ON external_ai_calls(mission_id);
CREATE INDEX IF NOT EXISTS idx_external_ai_calls_approved ON external_ai_calls(approved);
CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items(type);
CREATE INDEX IF NOT EXISTS idx_memory_items_approved ON memory_items(approved);
CREATE INDEX IF NOT EXISTS idx_validation_results_mission_id ON validation_results(mission_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_missions_updated_at BEFORE UPDATE ON missions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_memory_items_updated_at BEFORE UPDATE ON memory_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial configuration
INSERT INTO memory_items (type, title, content, approved, approved_by, category) VALUES
('glossary', 'Mission', 'A development task that involves planning, execution, validation, integration, and memory updates.', true, 'system', 'core'),
('glossary', 'Agent', 'A specialized AI worker with specific tools and responsibilities (e.g., Frontend Developer, Backend Developer).', true, 'system', 'core'),
('glossary', 'Orchestrator', 'The main agent responsible for planning, delegating, and coordinating all other agents.', true, 'system', 'core'),
('glossary', 'RAG', 'Retrieval-Augmented Generation: using vector search to inject relevant context into LLM prompts.', true, 'system', 'core');
