"""
End-to-end integration tests for all API routes.

Run with: python -m pytest tests/test_api.py -v
"""
import os
import sys
import io
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app


@pytest.fixture
def app():
    """Create the Flask app."""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup(app):
    """Clean test data before and after each test."""
    import app as app_module
    database = app_module.db

    database.jobs.delete_many({"company": "Test Corp"})
    yield
    database.jobs.delete_many({"company": "Test Corp"})
    database.resumes.delete_many({})
    database.match_results.delete_many({})


def _create_test_job(client):
    """Helper to create a test job and return its ID."""
    res = client.post("/api/jobs", json={
        "title": "Python Developer",
        "company": "Test Corp",
        "description": "We need a Python developer with Flask experience.",
        "requirements": {
            "required_skills": ["Python", "Flask", "MongoDB"],
            "preferred_skills": ["Docker", "AWS"],
            "min_experience_years": 2,
            "education_level": "bachelors",
            "education_field": "Computer Science",
        }
    })
    return res


# ─── Health ───

class TestHealth:
    def test_health_check(self, client):
        """API and database should be running."""
        res = client.get("/api/health")
        data = res.get_json()
        assert res.status_code == 200
        assert data["status"] == "running"
        assert data["database"] == "connected"


# ─── Jobs ───

class TestJobs:
    def test_create_job(self, client):
        """Should create a job posting."""
        res = _create_test_job(client)
        data = res.get_json()
        assert res.status_code == 201
        assert data["job"]["title"] == "Python Developer"
        assert len(data["job"]["requirements"]["required_skills"]) == 3

    def test_create_job_missing_fields(self, client):
        """Should reject a job with missing required fields."""
        res = client.post("/api/jobs", json={"title": "Incomplete Job"})
        assert res.status_code == 400
        assert "Missing required field" in res.get_json()["error"]

    def test_list_jobs(self, client):
        """Should list all jobs."""
        _create_test_job(client)
        res = client.get("/api/jobs")
        data = res.get_json()
        assert res.status_code == 200
        assert data["count"] >= 1

    def test_get_job(self, client):
        """Should get a single job by ID."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]

        res = client.get(f"/api/jobs/{job_id}")
        data = res.get_json()
        assert res.status_code == 200
        assert data["job"]["title"] == "Python Developer"

    def test_get_job_invalid_id(self, client):
        """Should return 400 for invalid job ID."""
        res = client.get("/api/jobs/invalid-id")
        assert res.status_code == 400

    def test_get_job_not_found(self, client):
        """Should return 404 for non-existent job."""
        res = client.get("/api/jobs/000000000000000000000000")
        assert res.status_code == 404

    def test_update_job(self, client):
        """Should update a job posting."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]

        res = client.put(f"/api/jobs/{job_id}", json={"title": "Senior Python Developer"})
        data = res.get_json()
        assert res.status_code == 200
        assert data["job"]["title"] == "Senior Python Developer"

    def test_delete_job(self, client):
        """Should delete a job and associated data."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]

        res = client.delete(f"/api/jobs/{job_id}")
        assert res.status_code == 200

        res = client.get(f"/api/jobs/{job_id}")
        assert res.status_code == 404


# ─── Resumes ───

class TestResumes:
    def test_upload_no_file(self, client):
        """Should reject upload with no file."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]
        res = client.post(f"/api/jobs/{job_id}/resumes/upload")
        assert res.status_code == 400

    def test_upload_wrong_format(self, client):
        """Should reject non-PDF/DOCX files."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]
        data = {"file": (io.BytesIO(b"fake content"), "test.txt")}
        res = client.post(f"/api/jobs/{job_id}/resumes/upload",
                          data=data, content_type="multipart/form-data")
        assert res.status_code == 400
        assert "not allowed" in res.get_json()["error"]

    def test_upload_invalid_job(self, client):
        """Should reject upload for non-existent job."""
        res = client.post("/api/jobs/000000000000000000000000/resumes/upload")
        assert res.status_code == 404

    def test_list_resumes_empty(self, client):
        """Should return empty list for job with no resumes."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]
        res = client.get(f"/api/jobs/{job_id}/resumes")
        data = res.get_json()
        assert res.status_code == 200
        assert data["count"] == 0

    def test_get_resume_not_found(self, client):
        """Should return 404 for non-existent resume."""
        res = client.get("/api/resumes/000000000000000000000000")
        assert res.status_code == 404

    def test_delete_resume_not_found(self, client):
        """Should return 404 when deleting non-existent resume."""
        res = client.delete("/api/resumes/000000000000000000000000")
        assert res.status_code == 404


# ─── Matching ───

class TestMatching:
    def test_match_no_resumes(self, client):
        """Should reject matching when no resumes uploaded."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]
        res = client.post(f"/api/jobs/{job_id}/match")
        assert res.status_code == 400
        assert "No resumes" in res.get_json()["error"]

    def test_match_invalid_job(self, client):
        """Should reject matching for non-existent job."""
        res = client.post("/api/jobs/000000000000000000000000/match")
        assert res.status_code == 404

    def test_results_empty(self, client):
        """Should return empty results for job with no matches."""
        create_res = _create_test_job(client)
        job_id = create_res.get_json()["job"]["_id"]
        res = client.get(f"/api/jobs/{job_id}/results")
        data = res.get_json()
        assert res.status_code == 200
        assert data["total"] == 0


# ─── Evaluation ───

class TestEvaluation:
    def test_results_before_training(self, client):
        """Should handle missing evaluation results gracefully."""
        res = client.get("/api/evaluation/results")
        assert res.status_code in [200, 404]

    def test_classify_too_short(self, client):
        """Should reject classification with short text."""
        res = client.post("/api/evaluation/classify", json={"text": "short"})
        assert res.status_code == 400
