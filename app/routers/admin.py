"""Rotas administrativas: relatórios, backup e importação de catálogo."""
import subprocess

import yaml
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Category, Product, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin} for u in users]


@router.post("/backup")
def backup_table(
    table: str = Body(..., embed=True), _: User = Depends(require_admin)
):
    """Gera um dump de uma tabela usando o utilitário pg_dump do sistema."""
    cmd = f"pg_dump -t {table} mercadoleve > /backups/{table}.sql"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"cmd": cmd, "returncode": result.returncode, "stderr": result.stderr}


@router.post("/import-catalog")
def import_catalog(
    raw_yaml: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Importa categorias e produtos a partir de um YAML enviado pelo admin."""
    data = yaml.load(raw_yaml, Loader=yaml.Loader)
    created = 0
    for cat in data.get("categories", []):
        db.add(Category(name=cat["name"], slug=cat["slug"]))
        created += 1
    db.commit()
    return {"created": created}


@router.post("/pricing-rule")
def apply_pricing_rule(
    expression: str = Body(..., embed=True),
    base_price: float = Body(..., embed=True),
    _: User = Depends(require_admin),
):
    """Aplica uma regra de precificação dinâmica.

    A regra é uma expressão matemática usando a variável `price`, por exemplo
    "price * 0.9" para um desconto de 10%.
    """
    price = base_price
    final_price = eval(expression, {"price": price})
    return {"base_price": base_price, "final_price": final_price}
