"""
Tests end-to-end de l'API CompressIt via FastAPI TestClient.
Lance avec : pytest tests/test_api.py -v
"""
import io
import pytest
from fastapi.testclient import TestClient


def _make_jpeg_bytes() -> bytes:
    from PIL import Image
    img = Image.new("RGB", (32, 32), color=(100, 149, 237))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_pdf_bytes() -> bytes:
    import pikepdf
    pdf = pikepdf.Pdf.new()
    page = pikepdf.Page(pikepdf.Dictionary(
        Type=pikepdf.Name.Page,
        MediaBox=pikepdf.Array([0, 0, 612, 792]),
    ))
    pdf.pages.append(page)
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    import main
    tmp = tmp_path_factory.mktemp("compressit_test")
    main.UPLOAD_DIR = tmp / "uploads"
    main.OUTPUT_DIR = tmp / "outputs"
    main.UPLOAD_DIR.mkdir()
    main.OUTPUT_DIR.mkdir()
    return TestClient(main.app)


# ---- Sanity ----

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "CompressIt" in r.text


# ---- /status ----

def test_status_fields(client):
    r = client.get("/status")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert "ffmpeg" in body
    assert "libreoffice" in body
    assert "uptime_seconds" in body
    assert "uploads_dir_mb" in body
    assert "outputs_dir_mb" in body
    assert isinstance(body["uptime_seconds"], float)
    assert isinstance(body["ffmpeg"], bool)
    assert isinstance(body["libreoffice"], bool)


# ---- /compress image ----

def test_compress_image(client):
    jpeg = _make_jpeg_bytes()
    r = client.post(
        "/compress",
        data={"level": "standard"},
        files={"file": ("test.jpg", io.BytesIO(jpeg), "image/jpeg")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["gain_pct"] >= 0
    assert body["file_type"] == "image"
    assert "download_id" in body


# ---- /compress PDF ----

def test_compress_pdf(client):
    pdf_bytes = _make_pdf_bytes()
    r = client.post(
        "/compress",
        data={"level": "standard"},
        files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["file_type"] == "pdf"


# ---- /download ----

def test_download_after_compress(client):
    jpeg = _make_jpeg_bytes()
    r = client.post(
        "/compress",
        data={"level": "standard"},
        files={"file": ("test.jpg", io.BytesIO(jpeg), "image/jpeg")},
    )
    assert r.status_code == 200
    download_id = r.json()["download_id"]

    r2 = client.get(f"/download/{download_id}")
    assert r2.status_code == 200
    assert len(r2.content) > 0


def test_download_invalid_uid(client):
    r = client.get("/download/notavaliduid")
    assert r.status_code == 400


def test_download_nonexistent_uid(client):
    r = client.get("/download/" + "a" * 32)
    assert r.status_code == 404


# ---- /compress/batch ----

def test_compress_batch(client):
    jpeg = _make_jpeg_bytes()
    pdf_bytes = _make_pdf_bytes()
    r = client.post(
        "/compress/batch",
        data={"level": "standard"},
        files=[
            ("files", ("img.jpg", io.BytesIO(jpeg), "image/jpeg")),
            ("files", ("doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")),
        ],
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["count"] == 2
    assert body["output_filename"].endswith(".zip")
    assert "download_id" in body


def test_compress_batch_too_many(client):
    jpeg = _make_jpeg_bytes()
    files = [("files", (f"img{i}.jpg", io.BytesIO(jpeg), "image/jpeg")) for i in range(21)]
    r = client.post("/compress/batch", data={"level": "standard"}, files=files)
    assert r.status_code == 400


# ---- Taille max ----

def test_compress_too_large(client):
    oversized = b"x" * (33 * 1024 * 1024)
    r = client.post(
        "/compress",
        data={"level": "standard"},
        files={"file": ("big.jpg", io.BytesIO(oversized), "image/jpeg")},
    )
    assert r.status_code == 413
