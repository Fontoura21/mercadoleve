"""Rotas administrativas: relatórios, backup e importação de catálogo."""
import ast
import operator
import re
import subprocess

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Category, Product, User

router = APIRouter(prefix="/admin", tags=["admin"])

# Tabelas que podem ser exportadas (lista de permissão).
ALLOWED_TABLES = {"users", "products", "orders", "categories", "reviews"}


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin} for u in users]


@router.post("/backup")
def backup_table(
    table: str = Body(..., embed=True), _: User = Depends(require_admin)
):
    """Gera um dump de uma tabela usando o utilitário pg_dump do sistema."""
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="Tabela não permitida")
    # Sem shell=True e com argumentos como lista: nenhum metacaractere é
    # interpretado pelo shell.
    result = subprocess.run(
        ["pg_dump", "-t", table, "-f", f"/backups/{table}.sql", "mercadoleve"],
        capture_output=True,
        text=True,
    )
    return {"table": table, "returncode": result.returncode}


@router.post("/import-catalog")
def import_catalog(
    raw_yaml: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Importa categorias a partir de um YAML enviado pelo admin."""
    # safe_load não instancia objetos Python arbitrários.
    data = yaml.safe_load(raw_yaml)
    created = 0
    for cat in (data or {}).get("categories", []):
        db.add(Category(name=cat["name"], slug=cat["slug"]))
        created += 1
    db.commit()
    return {"created": created}


# Operadores aritméticos seguros permitidos nas regras de preço.
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _safe_arith(node, price: float) -> float:
    """Avalia uma expressão aritmética simples sobre a variável `price`."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "price":
        return price
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](
            _safe_arith(node.left, price), _safe_arith(node.right, price)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_arith(node.operand, price))
    raise ValueError("Expressão não permitida")


@router.post("/pricing-rule")
def apply_pricing_rule(
    expression: str = Body(..., embed=True),
    base_price: float = Body(..., embed=True),
    _: User = Depends(require_admin),
):
    """Aplica uma regra de precificação dinâmica e segura.

    Apenas operações aritméticas sobre a variável `price` são aceitas,
    por exemplo "price * 0.9" para um desconto de 10%.
    """
    if not re.fullmatch(r"[\d\s\.\+\-\*\/\(\)price]+", expression):
        raise HTTPException(status_code=400, detail="Expressão inválida")
    try:
        tree = ast.parse(expression, mode="eval")
        final_price = _safe_arith(tree.body, base_price)
    except (ValueError, SyntaxError):
        raise HTTPException(status_code=400, detail="Expressão inválida")
    return {"base_price": base_price, "final_price": final_price}
