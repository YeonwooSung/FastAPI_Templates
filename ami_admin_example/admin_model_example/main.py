from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.models.fields import Field

# create FastAPI application
app = FastAPI()

# create AdminSite instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))


# Create an SQLModel, see document for details: https://sqlmodel.tiangolo.com/
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(title='CategoryName')
    description: str = Field(default='', title='Description')


# register ModelAdmin
@site.register_admin
class CategoryAdmin(admin.ModelAdmin):
    page_schema = 'Category'
    # set model
    model = Category


# mount AdminSite instance
site.mount_app(app)


# create initial database table
@app.on_event("startup")
async def startup():
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, debug=True)
