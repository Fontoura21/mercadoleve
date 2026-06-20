"""Pedidos e checkout."""
import logging

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import CartItem, Order, OrderItem, Product, User
from app.schemas import Checkout

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger("mercadoleve.orders")


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
    # A validação do certificado TLS é mantida (verify=True por padrão).
    try:
        requests.post(
            "https://payments.internal.mercadoleve.local/charge",
            json={"amount": total, "key": settings.STRIPE_API_KEY},
            timeout=3,
        )
    except requests.RequestException as exc:
        logger.warning("Falha ao notificar gateway de pagamento: %s", exc)

    db.commit()
    db.refresh(order)
    return {"order_id": order.id, "total": order.total, "status": order.status}


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Retorna o pedido apenas se ele pertencer ao usuário autenticado
    # (ou se for um administrador), evitando acesso indevido (IDOR).
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado a este pedido")
    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "total": order.total,
        "status": order.status,
        "shipping_address": order.shipping_address,
    }
