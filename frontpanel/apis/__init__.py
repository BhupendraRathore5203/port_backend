from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from frontpanel.apis.controller import PublicController
from .test_controller import TestController

# Create API instance
api = NinjaExtraAPI(
    title="My API",
    version="1.0.0",
    description="API documentation",
    docs_url="/docs",  # This creates /api/v1/docs
    openapi_url="/openapi.json",
    csrf=False,  # TODO: Set to True in production with proper frontend integration
)

# Register JWT authentication
api.register_controllers(NinjaJWTDefaultController)

# Register your controllers
api.register_controllers(
    TestController,
    PublicController,
    # AdminController,
    # UploadController,

)