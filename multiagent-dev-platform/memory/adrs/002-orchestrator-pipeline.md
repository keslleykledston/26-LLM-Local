# ADR 002: Fixed Orchestrator Pipeline

## Status
Accepted

## Context
We need a reliable, predictable process for executing development missions that ensures quality and consistency.

## Decision
The Orchestrator will follow a **fixed 5-phase pipeline**:

### Pipeline Phases

#### 1. PLAN
- Break mission into tasks
- Query RAG memory for relevant context
- Assign tasks to specialized agents
- Create execution plan

#### 2. EXECUTE
- Delegate tasks to agents
- Monitor execution
- Collect results
- Handle failures

#### 3. VALIDATE
- Run linting (eslint, flake8, black)
- Run tests (pytest, jest)
- Run builds (npm build, webpack)
- **Reject if any validation fails**

#### 4. INTEGRATE
- Create feature branch
- Commit changes with descriptive message
- Update documentation
- Prepare for review

#### 5. MEMORY
- Create mission summary
- Extract learnings
- Update RAG knowledge base (pending approval)
- Link to relevant ADRs

## Consequences

### Positive
- **Quality assurance**: Nothing merges without passing validation
- **Consistency**: Same process for every mission
- **Traceability**: Clear audit trail
- **Knowledge accumulation**: Every mission improves the memory
- **Failure safety**: Validations catch issues early

### Negative
- **Longer execution**: Validation adds time
- **Stricter requirements**: May block valid work if tests are brittle
- **Setup dependency**: Requires working lint/test/build setup

## Implementation Notes
- Validation phase is **mandatory** and **blocking**
- If validation fails, mission status → `failed`
- Memory updates require manual approval before embedding
- Each phase logs detailed execution info
