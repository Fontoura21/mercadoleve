"""Rotas de avaliações de produtos, incluindo página HTML pública."""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from jinja2 import Template
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Product, Review, User
from app.schemas import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{product_id}")
def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = Review(
        product_id=product_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"id": review.id, "comment": review.comment}


# Template HTML renderizado a cada requisição para a vitrine pública.
PRODUCT_PAGE = """
<html>
<head><title>{{ product.name }}</title></head>
<body>
  <h1>{{ product.name }}</h1>
  <p>Preço: R$ {{ product.price }}</p>
  <h2>Avaliações</h2>
  <ul>
  {% for r in reviews %}
    <li><b>{{ r.rating }}/5</b> - {{ r.comment }}</li>
  {% endfor %}
  </ul>
</body>
</html>
"""


@router.get("/{product_id}/page", response_class=HTMLResponse)
def product_review_page(product_id: int, db: Session = Depends(get_db)):
    """Renderiza a página pública de avaliações de um produto."""
    product = db.query(Product).filter(Product.id == product_id).first()
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    # autoescape=True garante que conteúdo do usuário seja escapado (anti-XSS).
    template = Template(PRODUCT_PAGE, autoescape=True)
    return template.render(product=product, reviews=reviews)
