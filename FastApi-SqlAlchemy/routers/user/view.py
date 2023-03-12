from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional, List
from  routers.user.serializer import UserBase
from  routers.user import models
import time
from connection_pool import database_instance

router = APIRouter(
    prefix="/users",
    tags=['user']
)



# Create a new area
@router.get("/", status_code=status.HTTP_201_CREATED)
async def get_user():
    """ 
    This function is to get all users
    """
    try:
        value = await database_instance.fetch_rows(query="SELECT * FROM public.user")
        return  value
    except Exception as err:
        print(err.args[0])
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=err.args[0])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase):
    db_user = models.User(**dict(user))
    result = await database_instance.execute(
        query="INSERT INTO public.user (id, fname,lname, email, password) VALUES ('{}', '{}', '{}', '{}', '{}')".format(db_user.id, db_user.fname,db_user.lname, db_user.email, db_user.password))
    if result == "INSERT 0 1":
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong")
    
