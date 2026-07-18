import pytest

@pytest.mark.asyncio
async def test_health_check(app_client):
    """Test the health check endpoint returns 200 OK and expected structure."""
    response = app_client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] in ("healthy", "degraded", "unhealthy")
    assert "app" in data["components"]
    assert data["components"]["app"]["status"] == "healthy"
