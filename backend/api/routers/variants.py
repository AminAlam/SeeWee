from __future__ import annotations

import io
import os
import subprocess
import tempfile
import zipfile
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.db import db_session
from core.exporters.latex_exporter import render_latex_template
from core.exporters.html_exporter import render_academicpages_like_preview, render_html_bundle
from core.exporters.linkedin_exporter import render_linkedin_bundle
from core.variant_engine import build_variant_document, build_variant_preview
from core.repos.variants_repo import VariantRecord, VariantsRepo
from core.repos.profile_repo import ProfileRepo

router = APIRouter(prefix="/variants", tags=["variants"])


class VariantCreateIn(BaseModel):
    name: str = Field(min_length=1)
    rules: dict[str, Any] = Field(default_factory=dict)
    sections: list[str] = Field(default_factory=list)


class VariantUpdateIn(BaseModel):
    name: str | None = None
    rules: dict[str, Any] | None = None
    sections: list[str] | None = None


class VariantOut(BaseModel):
    id: str
    name: str
    rules: dict[str, Any]
    sections: list[str]
    created_at: str
    updated_at: str
    has_layout: bool = False


class VariantPreviewOut(BaseModel):
    variant_id: str
    generated_at: str
    sections: list[dict]


class LayoutIn(BaseModel):
    """Layout input: sections with ordered entry IDs."""
    sections: dict[str, list[str]]  # section_id -> [entry_id, ...]


class LayoutOut(BaseModel):
    """Layout output."""
    variant_id: str
    sections: dict[str, list[str]]


def _to_out(v: VariantRecord) -> VariantOut:
    return VariantOut(
        id=v.id,
        name=v.name,
        rules=v.rules,
        sections=[s for (s, _pos) in v.sections],
        created_at=v.created_at.isoformat(),
        updated_at=v.updated_at.isoformat(),
        has_layout=v.layout is not None,
    )


@router.get("")
def list_variants(db: Session = Depends(db_session)) -> list[VariantOut]:
    repo = VariantsRepo(db)
    return [_to_out(v) for v in repo.list()]


@router.post("")
def create_variant(payload: VariantCreateIn, db: Session = Depends(db_session)) -> VariantOut:
    repo = VariantsRepo(db)
    v = repo.create(name=payload.name, rules=payload.rules, sections=payload.sections)
    return _to_out(v)


@router.get("/{variant_id}")
def get_variant(variant_id: str, db: Session = Depends(db_session)) -> VariantOut:
    repo = VariantsRepo(db)
    try:
        return _to_out(repo.get(variant_id))
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")


@router.get("/{variant_id}/preview")
def preview_variant(variant_id: str, db: Session = Depends(db_session)) -> dict:
    try:
        return build_variant_preview(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")


@router.post("/{variant_id}/export/latex")
def export_variant_latex(variant_id: str, db: Session = Depends(db_session)) -> StreamingResponse:
    try:
        doc = build_variant_document(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    profile = ProfileRepo(db).get().data
    tex = render_latex_template(doc, profile)

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("main.tex", tex)
        zf.writestr(
            "README.txt",
            "SeeWee LaTeX export\n\nCompile with:\n  pdflatex main.tex\n",
        )
    mem.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="seewee-{variant_id}.zip"'}
    return StreamingResponse(mem, media_type="application/zip", headers=headers)


@router.get("/{variant_id}/preview/pdf")
def preview_variant_pdf(variant_id: str, db: Session = Depends(db_session)) -> StreamingResponse:
    try:
        doc = build_variant_document(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    profile = ProfileRepo(db).get().data
    tex = render_latex_template(doc, profile)

    with tempfile.TemporaryDirectory(prefix="seewee-tex-") as td:
        tex_path = os.path.join(td, "main.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        # Use latexmk to build PDF.
        # This runs inside the API container, which has texlive + latexmk installed.
        proc = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=td,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={"error": "latex build failed", "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]},
            )

        pdf_path = os.path.join(td, "main.pdf")
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="pdf not generated")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


@router.post("/{variant_id}/export/html")
def export_variant_html(variant_id: str, db: Session = Depends(db_session)) -> StreamingResponse:
    try:
        doc = build_variant_document(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    bundle = render_html_bundle(doc)

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in bundle.items():
            zf.writestr(name, content)
        zf.writestr(
            "README.txt",
            "SeeWee HTML export\n\nOpen index.html in a browser.\nNote: this MVP uses React from a CDN.\n",
        )
    mem.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="seewee-{variant_id}-html.zip"'}
    return StreamingResponse(mem, media_type="application/zip", headers=headers)


@router.get("/{variant_id}/preview/html")
def preview_variant_html(variant_id: str, db: Session = Depends(db_session)) -> StreamingResponse:
    try:
        doc = build_variant_document(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    profile = ProfileRepo(db).get().data
    html = render_academicpages_like_preview(doc, profile)
    return StreamingResponse(io.BytesIO(html.encode("utf-8")), media_type="text/html; charset=utf-8")


@router.post("/{variant_id}/export/linkedin")
def export_variant_linkedin(variant_id: str, db: Session = Depends(db_session)) -> StreamingResponse:
    try:
        doc = build_variant_document(db, variant_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    bundle = render_linkedin_bundle(doc)

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in bundle.items():
            zf.writestr(name, content)
    mem.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="seewee-{variant_id}-linkedin.zip"'}
    return StreamingResponse(mem, media_type="application/zip", headers=headers)


@router.put("/{variant_id}")
def update_variant(variant_id: str, payload: VariantUpdateIn, db: Session = Depends(db_session)) -> VariantOut:
    repo = VariantsRepo(db)
    try:
        return _to_out(
            repo.update(variant_id, name=payload.name, rules=payload.rules, sections=payload.sections)
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")


@router.delete("/{variant_id}")
def delete_variant(variant_id: str, db: Session = Depends(db_session)) -> dict[str, str]:
    repo = VariantsRepo(db)
    repo.delete(variant_id)
    return {"status": "ok"}


@router.get("/{variant_id}/layout")
def get_variant_layout(variant_id: str, db: Session = Depends(db_session)) -> LayoutOut:
    """Get the manual layout for a variant."""
    repo = VariantsRepo(db)
    try:
        repo.get(variant_id)  # Verify variant exists
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    layout = repo.get_layout(variant_id)
    return LayoutOut(
        variant_id=variant_id,
        sections=layout.sections if layout else {},
    )


@router.put("/{variant_id}/layout")
def set_variant_layout(variant_id: str, payload: LayoutIn, db: Session = Depends(db_session)) -> LayoutOut:
    """Set the manual layout for a variant."""
    repo = VariantsRepo(db)
    try:
        repo.get(variant_id)  # Verify variant exists
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    layout = repo.set_layout(variant_id, payload.sections)
    return LayoutOut(
        variant_id=variant_id,
        sections=layout.sections,
    )


@router.delete("/{variant_id}/layout")
def clear_variant_layout(variant_id: str, db: Session = Depends(db_session)) -> dict[str, str]:
    """Clear the manual layout for a variant (revert to auto-grouping)."""
    repo = VariantsRepo(db)
    try:
        repo.get(variant_id)  # Verify variant exists
    except NoResultFound:
        raise HTTPException(status_code=404, detail="variant not found")

    repo.clear_layout(variant_id)
    return {"status": "ok"}


