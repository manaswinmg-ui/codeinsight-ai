from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.repository import (
    FileReviewResponse,
    RepositoryDetailResponse,
    RepositoryResponse,
)


@pytest.mark.asyncio
async def test_upload_repository_endpoint(client: AsyncClient) -> None:
    """Test repository upload endpoint successfully triggers backend."""
    mock_response = RepositoryResponse(
        repository_id=456, status="PENDING", created_at=datetime.now(UTC)
    )

    # Mock the app service call
    with patch(
        "app.application.repository_analysis_service.repository_analysis_service.submit_repository",
        new_callable=AsyncMock,
    ) as mock_submit:
        mock_submit.return_value = mock_response

        # Generate fake zip file payload
        import io
        import zipfile

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("main.py", "print('hello')")
        zip_bytes = zip_buffer.getvalue()

        # Send request
        files = {"file": ("project.zip", zip_bytes, "application/zip")}
        response = await client.post("/api/v1/repositories", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["repository_id"] == 456
        assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_get_repository_detail_endpoint(client: AsyncClient) -> None:
    """Test retrieval of repository detailed metrics."""
    mock_detail = RepositoryDetailResponse(
        id=456,
        name="project.zip",
        status="COMPLETED",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        language_summary={"python": 1},
        overall_quality=95,
        summary="Looks clean",
        files_analyzed=1,
        critical_findings=0,
        open_tickets=0,
        duration_seconds=5.2,
        files=[
            FileReviewResponse(
                id=12,
                file_path="main.py",
                language="python",
                status="COMPLETED",
                quality_score=95,
                findings_count=0,
                tickets_count=0,
            )
        ],
        largest_files=[{"file_path": "main.py", "size_bytes": 100}],
        most_problematic_files=[],
    )

    with patch(
        "app.application.repository_analysis_service.repository_analysis_service.get_repository_detail",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_detail

        response = await client.get("/api/v1/repositories/456")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 456
        assert data["name"] == "project.zip"
        assert data["overall_quality"] == 95
        assert len(data["files"]) == 1
        assert data["files"][0]["file_path"] == "main.py"


@pytest.mark.asyncio
async def test_get_repository_detail_not_found(client: AsyncClient) -> None:
    """Test 404 response for non-existent repository."""
    with patch(
        "app.application.repository_analysis_service.repository_analysis_service.get_repository_detail",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None

        response = await client.get("/api/v1/repositories/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Repository review with ID 999 not found."


@pytest.mark.asyncio
async def test_query_repository_endpoint(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test query repository endpoint successfully routes and returns answer."""
    from app.models.repository import Repository

    mock_repo = MagicMock(spec=Repository)
    mock_repo.id = 456

    mock_result = {
        "answer": "Mocked answer",
        "model_used": "gpt-4o-mini",
        "cost": 0.0001,
        "escalated": False,
        "reason": "Test route",
        "files_retrieved": ["src/main.py"],
    }

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_repo

    mock_result_obj = MagicMock()
    mock_result_obj.scalars.return_value = mock_scalars
    db_session.execute = AsyncMock(return_value=mock_result_obj)

    with patch(
        "app.ai.router.AIRouter.query_repository", new_callable=AsyncMock
    ) as mock_query:
        mock_query.return_value = mock_result

        payload = {"question": "What is this?"}
        response = await client.post("/api/v1/repositories/456/query", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Mocked answer"
        assert data["model_used"] == "gpt-4o-mini"
        assert data["escalated"] is False
        assert data["files_retrieved"] == ["src/main.py"]


@pytest.mark.asyncio
async def test_query_repository_endpoint_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test query repository endpoint returns 404 if repository does not exist."""
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None

    mock_result_obj = MagicMock()
    mock_result_obj.scalars.return_value = mock_scalars
    db_session.execute = AsyncMock(return_value=mock_result_obj)

    payload = {"question": "What is this?"}
    response = await client.post("/api/v1/repositories/999/query", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository review with ID 999 not found."


@pytest.mark.asyncio
async def test_scan_repository_upload_endpoint(client: AsyncClient) -> None:
    """Test POST /api/v1/repositories/upload endpoint returns ScanResult without db session needed."""
    import io
    import zipfile

    # Create zip bytes in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("src/main.py", b"print('hello')")
        zf.writestr("README.md", b"# Docs")
    zip_bytes = buf.getvalue()

    response = await client.post(
        "/api/v1/repositories/upload",
        files={"file": ("repo.zip", zip_bytes, "application/zip")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "manifest" in data
    assert "tree" in data

    manifest = data["manifest"]
    assert manifest["repository_name"] == "repo.zip"

    stats = manifest["statistics"]
    assert stats["total_files"] == 2
    assert stats["supported_files"] == 1
    assert stats["unsupported_files"] == 1
