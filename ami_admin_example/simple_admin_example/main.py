from fastapi import FastAPI

from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite


# create the app
app = FastAPI()

# create the admin site
site = AdminSite(settings=Settings(database_url_async="sqlite+aiosqlite:///amisadmin.db"))

# mount the app
site.mount_app(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, debug=True)
