from flask_restx import Api, Resource, Namespace
from flask import Blueprint
from .user_resource import user

users_bp = Blueprint('users_api', __name__)


api = Api(users_bp,
    title="Checkin Backend", 
    description="Uma api focada em dar suporte ao front-end do checkin",
    prefix="/api",
)

ns = Namespace("info", description="Information about the application and data status")


@ns.route("/healthcheck")
class HealthCheck(Resource):
    def get(self) -> None:
        return {"status":"ok"}
    
    
    

    
api.add_namespace(user)
api.add_namespace(ns)
    
__all__ = [api]