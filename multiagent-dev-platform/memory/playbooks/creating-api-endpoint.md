# Playbook: Creating a New API Endpoint

## Overview
Step-by-step guide for creating a new REST API endpoint in FastAPI.

## Prerequisites
- FastAPI project structure
- Database models defined
- Pydantic schemas created

## Steps

### 1. Define Pydantic Schema
```python
# app/schemas/resource.py
from pydantic import BaseModel, Field
from typing import Optional

class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ResourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True
```

### 2. Create API Router
```python
# app/api/v1/resources.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceResponse

router = APIRouter()

@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new resource"""
    resource = Resource(**data.model_dump())
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource
```

### 3. Register Router
```python
# app/main.py
from app.api.v1 import resources

app.include_router(
    resources.router,
    prefix="/api/v1/resources",
    tags=["Resources"]
)
```

### 4. Add Tests
```python
# tests/test_resources.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resource(client: AsyncClient):
    response = await client.post(
        "/api/v1/resources/",
        json={"name": "Test Resource", "description": "Test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Resource"
```

## Best Practices
- Always use Pydantic for validation
- Use async/await for database operations
- Include proper error handling
- Write tests for all endpoints
- Document with docstrings
- Use proper HTTP status codes

## Common Pitfalls
- Forgetting to refresh after commit
- Not using `from_attributes = True` in Config
- Missing async/await keywords
- Not handling exceptions properly
