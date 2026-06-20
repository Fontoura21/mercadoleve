"""Carrinho de compras."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import AddToCart

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("")
def view_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    return [
        {"id": i.id, "product_id": i.product_id, "quantity": i.quantity} for i in items
    ]


@router.post("/add")
def add_to_cart(
    payload: AddToCart,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    item = CartItem(
        user_id=user.id, product_id=payload.product_id, quantity=payload.quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "product_id": item.product_id, "quantity": item.quantity}


@router.delete("/item/{item_id}")
def remove_item(
    item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    # Remove um item do carrinho, restrito ao carrinho do próprio usuário.
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return {"removed": item_id}
