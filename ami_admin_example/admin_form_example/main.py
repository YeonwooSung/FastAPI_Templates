from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from fastapi_amis_admin.amis.components import Form
from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.crud.schema import BaseApiOut
from fastapi_amis_admin.models.fields import Field


# create FastAPI application
app = FastAPI()

# create AdminSite instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))


# register FormAdmin
@site.register_admin
class UserLoginFormAdmin(admin.FormAdmin):
    page_schema = 'UserLoginForm'
    # set form information, optional
    form = Form(title='This is a test login form', submitText='login')

    # create form schema
    class schema(BaseModel):
        username: str = Field(..., title='username', min_length=3, max_length=30)
        password: str = Field(..., title='password')

    # handle form submission data
    async def handle(self, request: Request, data: BaseModel, **kwargs) -> BaseApiOut[Any]:
        if data.username == 'amisadmin' and data.password == 'amisadmin':
            return BaseApiOut(msg='Login successfully!', data={'token': 'xxxxxx'})
        return BaseApiOut(status=-1, msg='Incorrect username or password!')


# mount AdminSite instance
site.mount_app(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, debug=True)
