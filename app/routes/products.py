from pydantic import BaseModel
from typing import List, Optional


class PriceFilter(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None


class ProductQuery(BaseModel):
    category: Optional[str] = None
    brands: Optional[List[str]] = None
    price: Optional[PriceFilter] = None
    rating: Optional[float] = None


from fastapi import FastAPI,Body, Request,APIRouter
from fastapi.responses import JSONResponse
# from models import ProductQuery

router = APIRouter()

products = [
    {
        "id": 1,
        "name": "iPhone 16",
        "brand": "Apple",
        "category": "electronics",
        "price": 900,
        "rating": 4.8
    },
    {
        "id": 2,
        "name": "Galaxy S25",
        "brand": "Samsung",
        "category": "electronics",
        "price": 850,
        "rating": 4.6
    },
    {
        "id": 3,
        "name": "MacBook Pro",
        "brand": "Apple",
        "category": "electronics",
        "price": 2200,
        "rating": 4.9
    }
]


def filter_products(query: ProductQuery):
    result = products

    if query.category:
        result = [
            p for p in result
            if p["category"] == query.category
        ]

    if query.brands:
        result = [
            p for p in result
            if p["brand"] in query.brands
        ]

    if query.price:
        if query.price.min is not None:
            result = [
                p for p in result
                if p["price"] >= query.price.min
            ]

        if query.price.max is not None:
            result = [
                p for p in result
                if p["price"] <= query.price.max
            ]

    if query.rating:
        result = [
            p for p in result
            if p["rating"] >= query.rating
        ]

    return result


@router.get("/products")
def get_products():
    return products


@router.post("/products/search")
def search_products(query: ProductQuery):
    return filter_products(query)


@router.api_route(
    "/products",
    methods=["QUERY"]
)
async def query_products(
    request: Request,
    query: ProductQuery = Body(...)
):
    result = filter_products(query)

    return JSONResponse(
        content={
            "method": request.method,
            "safe": True,
            "results": result
        }
    )
