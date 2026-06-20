"""Rotas de produtos: listagem, busca e cadastro."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Product, User
from app.schemas import ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()


# Colunas permitidas para ordenação (lista de permissão).
ALLOWED_ORDER = {"name", "price", "stock", "id"}


@router.get("/search")
def search_products(q: str = "", order: str = "name", db: Session = Depends(get_db)):
    """Busca produtos por nome ou descrição.

    A consulta usa parâmetros vinculados (bind parameters) e uma lista de
    permissão para a coluna de ordenação, evitando injeção de SQL.
    """
    if order not in ALLOWED_ORDER:
        order = "name"
    sql = text(
        "SELECT id, name, description, price, stock "
        "FROM products "
        "WHERE name ILIKE :pattern OR description ILIKE :pattern "
        f"ORDER BY {order}"
    )
    rows = db.execute(sql, {"pattern": f"%{q}%"}).fetchall()
    return [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "price": r[3],
            "stock": r[4],
        }
        for r in rows
    ]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.post("", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user.is_seller and not user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas vendedores podem cadastrar")
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category_id=payload.category_id,
        image_url=payload.image_url,
        seller_id=user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
