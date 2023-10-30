from fastapi import APIRouter, HTTPException, Depends
from typing import Union, List

from schemas import Product, ProductUpsert

router = APIRouter(prefix="/products")

fake_product_db = [
    Product(id=1, title="Plumbus", description=""),
    Product(id=2, title="Portal Gun", description="")
]


async def common_parameters(q: Union[str, None] = None, skip: int = 0, limit: int = 100):
    if skip < 0 or limit < 0:
        param_name = "skip and limit" if skip < 0 and limit < 0 else "skip" if skip < 0 else "limit"
        raise HTTPException(status_code=400, detail=f"The value for {param_name} cannot be less than 0")
    if limit > 999:
        raise HTTPException(status_code=400, detail="The maximum allowed value for limit is 999")
    return q, skip, limit


@router.get("/{product_id}")
async def read_product(product_id: int) -> Product:
    product = next((p for p in fake_product_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} does not exist")
    return product


@router.get("/")
async def list_products(commons: dict = Depends(common_parameters)) -> List[Product]:
    q, skip, limit = commons
    return fake_product_db[skip:limit]


@router.post("/", status_code=201)
async def create_product(product_create: ProductUpsert) -> Product:
    product_id = max([p.id for p in fake_product_db]) + 1
    product = Product(id=product_id, **product_create.dict())
    fake_product_db.append(product)
    return product


@router.put("/{product_id}")
async def update_product(product_id: int, product_update: ProductUpsert) -> Product:
    product = None
    for i in range(len(fake_product_db)):
        if fake_product_db[i].id == product_id:
            product = Product(id=product_id, **product_update.dict())
            fake_product_db[i] = product
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} does not exist")
    return product
