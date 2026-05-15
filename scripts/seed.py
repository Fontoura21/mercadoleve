"""Popula o banco com dados de exemplo para desenvolvimento e DAST."""
from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Category, Product, Review, User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(User).first():
        print("Banco já populado.")
        return

    admin = User(
        email="admin@mercadoleve.local",
        full_name="Administradora",
        password_hash=hash_password("admin123"),
        is_admin=True,
        is_seller=True,
    )
    seller = User(
        email="vendedor@mercadoleve.local",
        full_name="Vendedor Exemplo",
        password_hash=hash_password("senha123"),
        is_seller=True,
    )
    db.add_all([admin, seller])
    db.flush()

    cat = Category(name="Eletrônicos", slug="eletronicos")
    db.add(cat)
    db.flush()

    p1 = Product(
        name="Fone Bluetooth Pro",
        description="Fone sem fio com cancelamento de ruído",
        price=299.90,
        stock=50,
        seller_id=seller.id,
        category_id=cat.id,
    )
    p2 = Product(
        name="Carregador Turbo 65W",
        description="Carregador USB-C de carga rápida",
        price=129.90,
        stock=120,
        seller_id=seller.id,
        category_id=cat.id,
    )
    db.add_all([p1, p2])
    db.flush()

    db.add(Review(product_id=p1.id, user_id=admin.id, rating=5, comment="Excelente!"))
    db.commit()
    print("Seed concluído.")


if __name__ == "__main__":
    run()
