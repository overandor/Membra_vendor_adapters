"""MEMBRA Vendor Adapters — non-executing vendor package registry.

This app records vendor-ready package requests for MEMBRA media kits. It does not
call live vendor APIs. It creates auditable records that a human operator or a
future approved integration can process.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import gradio as gr
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_NAME = "MEMBRA Vendor Adapters"
DB_PATH = Path(os.getenv("APP_DB_PATH", "/tmp/membra_vendor_adapters.sqlite3"))
api = FastAPI(title=APP_NAME, version="1.0.0")
VENDORS = ["manual", "print_partner", "apparel_partner", "label_partner", "local_shop"]

class PackageRequest(BaseModel):
    vendor: str = "manual"
    package_type: str = "wearable_media_kit"
    subject_id: str
    recipient_email: str = ""
    sku: str = "custom"
    quantity: int = Field(default=1, ge=1)
    creative_url: str = ""
    qr_url: str = ""
    proof_requirements: str = "receipt confirmation and production proof"
    metadata: dict[str, Any] = Field(default_factory=dict)

class StatusUpdate(BaseModel):
    status: str = "queued"
    reference: str = ""
    notes: str = ""


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS packages(
          package_id TEXT PRIMARY KEY,
          vendor TEXT,
          package_type TEXT,
          subject_id TEXT,
          recipient_email TEXT,
          sku TEXT,
          quantity INTEGER,
          creative_url TEXT,
          qr_url TEXT,
          proof_requirements TEXT,
          status TEXT,
          reference TEXT,
          notes TEXT,
          metadata_json TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        """)

init_db()


def create_package(data: PackageRequest) -> dict[str, Any]:
    if data.vendor not in VENDORS:
        raise ValueError("unsupported vendor")
    ts = now()
    row = {
        "package_id": new_id("pkg"),
        "vendor": data.vendor,
        "package_type": data.package_type,
        "subject_id": data.subject_id,
        "recipient_email": data.recipient_email,
        "sku": data.sku,
        "quantity": data.quantity,
        "creative_url": data.creative_url,
        "qr_url": data.qr_url,
        "proof_requirements": data.proof_requirements,
        "status": "queued_for_operator_review",
        "reference": "",
        "notes": "",
        "metadata_json": json.dumps(data.metadata, default=str),
        "created_at": ts,
        "updated_at": ts,
    }
    with db() as conn:
        conn.execute("INSERT INTO packages VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
    return row


def update_package(package_id: str, data: StatusUpdate) -> dict[str, Any]:
    with db() as conn:
        found = conn.execute("SELECT * FROM packages WHERE package_id=?", (package_id,)).fetchone()
    if not found:
        raise HTTPException(404, "package not found")
    with db() as conn:
        conn.execute("UPDATE packages SET status=?, reference=?, notes=?, updated_at=? WHERE package_id=?", (data.status, data.reference, data.notes, now(), package_id))
        out = conn.execute("SELECT * FROM packages WHERE package_id=?", (package_id,)).fetchone()
    return dict(out)


def packages() -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM packages ORDER BY created_at DESC LIMIT 250").fetchall()
    return [dict(r) for r in rows]

@api.get("/api/health")
def health():
    return {"ok": True, "app": APP_NAME, "mode": "non-executing vendor package registry", "vendors": VENDORS}

@api.post("/api/packages")
def api_create(data: PackageRequest):
    try:
        return create_package(data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@api.post("/api/packages/{package_id}/status")
def api_status(package_id: str, data: StatusUpdate):
    return update_package(package_id, data)

@api.get("/api/packages")
def api_list():
    return {"packages": packages()}


def ui_create(vendor, package_type, subject_id, email, sku, qty, creative_url, qr_url, proof, metadata_json):
    try:
        metadata = json.loads(metadata_json or "{}")
        out = create_package(PackageRequest(vendor=vendor, package_type=package_type, subject_id=subject_id, recipient_email=email, sku=sku, quantity=int(qty or 1), creative_url=creative_url, qr_url=qr_url, proof_requirements=proof, metadata=metadata))
        return out, packages()
    except Exception as exc:
        return {"error": str(exc)}, packages()


def ui_status(package_id, status, reference, notes):
    try:
        return update_package(package_id, StatusUpdate(status=status, reference=reference, notes=notes)), packages()
    except Exception as exc:
        return {"error": str(exc)}, packages()

with gr.Blocks(title=APP_NAME) as demo:
    gr.Markdown("# MEMBRA Vendor Adapters\nNon-executing registry for vendor-ready package requests. Operators approve or process integrations separately.")
    with gr.Tab("Create package"):
        vendor = gr.Dropdown(VENDORS, value="manual", label="Vendor class")
        package_type = gr.Dropdown(["wearable_media_kit", "qr_label", "window_media", "event_badge", "manual_package"], value="wearable_media_kit", label="Package type")
        subject_id = gr.Textbox(label="Subject ID")
        email = gr.Textbox(label="Recipient email")
        sku = gr.Textbox(label="SKU", value="custom")
        qty = gr.Number(label="Quantity", value=1)
        creative_url = gr.Textbox(label="Creative URL")
        qr_url = gr.Textbox(label="QR URL")
        proof = gr.Textbox(label="Proof requirements", value="receipt confirmation and production proof")
        metadata = gr.Code(label="Metadata JSON", language="json", value="{}")
        create_btn = gr.Button("Create package request", variant="primary")
        create_out = gr.JSON(label="Package request")
    with gr.Tab("Status"):
        package_id = gr.Textbox(label="Package ID")
        status = gr.Dropdown(["queued", "operator_review", "approved", "in_progress", "completed", "blocked", "cancelled"], value="queued", label="Status")
        reference = gr.Textbox(label="Reference")
        notes = gr.Textbox(label="Notes", lines=3)
        status_btn = gr.Button("Update status", variant="primary")
        status_out = gr.JSON(label="Status update")
    table = gr.Dataframe(label="Package registry", value=packages, interactive=False)
    create_btn.click(ui_create, [vendor, package_type, subject_id, email, sku, qty, creative_url, qr_url, proof, metadata], [create_out, table])
    status_btn.click(ui_status, [package_id, status, reference, notes], [status_out, table])

app = gr.mount_gradio_app(api, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
