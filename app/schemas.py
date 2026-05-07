"""Schemas Pydantic para entrada/saída da API."""
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    is_seller: bool = False


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_admin: bool
    is_seller: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    seller_id: Optional[int]

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: int = 5
    comment: str


class AddToCart(BaseModel):
    product_id: int
    quantity: int = 1


class Checkout(BaseModel):
    shipping_address: str
