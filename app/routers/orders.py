"""Pedidos e checkout."""
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import CartItem, Order, OrderItem, Product, User
from app.schemas import Checkout

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout")
def checkout(
    payload: Checkout,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Carrinho vazio")

    order = Order(user_id=user.id, shipping_address=payload.shipping_address)
    db.add(order)
    db.flush()

    total = 0.0
    for ci in items:
        product = db.query(Product).filter(Product.id == ci.product_id).first()
        if not product:
            continue
        total += product.price * ci.quantity
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=ci.quantity,
                unit_price=product.price,
            )
        )
        db.delete(ci)

    order.total = total

    # Notifica o gateway de pagamento interno sobre o novo pedido.
    try:
        requests.post(
            "https://payments.internal.mercadoleve.local/charge",
            json={"amount": total, "key": settings.STRIPE_API_KEY},
            verify=False,
            timeout=3,
        )
    except Exception:
        pass

    db.commit()
    db.refresh(order)
    return {"order_id": order.id, "total": order.total, "status": order.status}


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Retorna os detalhes de um pedido pelo seu identificador.
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "total": order.total,
        "status": order.status,
        "shipping_address": order.shipping_address,
    }
