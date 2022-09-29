from flask import Blueprint, jsonify, request 
from main import db
from models.gallery import Gallery
from schemas.gallery_schema import gallery_schema, gallerys_schema
from models.admin import Admin
from datetime import date
from flask_jwt_extended import jwt_required, get_jwt_identity

gallerys = Blueprint('gallerys', __name__, url_prefix="/gallerys")

# The GET routes endpoint
@gallerys.route("/", methods=["GET"])
def get_gallerys():
    # get all gallerys from the database table
    gallerys_list = Gallery.query.all()
    # Convert the gallerys from the database into a JSON format and store them in result
    result = gallerys_schema.dump(gallerys_list)
    # return the data in JSON format
    return jsonify(result)

@gallerys.route("/<int:id>/", methods=["GET"])
def get_gallery(id):
    gallery = Gallery.query.get(id)
    # get a list of gallerys filtering by the given criteria, first will return the first match instead of a list
    gallery = Gallery.query.filter_by(gallery_id=id).first()
    # check if  we found a gallery
    if not gallery:
        return {"error": "Gallery not found"}
    # serialise the result in a single gallery schema
    return jsonify(gallery_schema.dump(gallery))

# The POST route endpoint
@gallerys.route("/", methods=["POST"])
# a token is required for this request
@jwt_required()
def new_gallery():
    # it's not enough with a token, the identity needs to be a admin
    if get_jwt_identity() != "admin":
        return {"error": "You don't have the permission to do this"}
    # add a new gallery
    gallery_fields = gallery_schema.load(request.json)
    gallery = Gallery.query.filter_by(name=gallery_fields["name"]).first()
    if gallery:
        return {"error": "Gallery already registered"}

    new_gallery = Gallery(
        name = gallery_fields["name"],
        location = gallery_fields["location"],
        phone_number = gallery_fields["phone_number"],
        open_hours = gallery_fields["open_hours"],
        description = gallery_fields["description"],
        admin_id = gallery_fields["admin_id"]
    )

    # add to the database and commit
    db.session.add(new_gallery)
    db.session.commit()

    #return the gallery in the response
    return jsonify(gallery_schema.dump(new_gallery))

# round out our CRUD resource with a DELETE method
@gallerys.route("/<int:id>/", methods=["DELETE"])
@jwt_required()
def delete_gallery(id):
    if get_jwt_identity() != "admin":
        return {"error": "You don't have the permission to do this"}
    gallery = Gallery.query.filter_by(id=id).first()
    #return an error if the card doesn't exist
    if not gallery:
        return {"error": "Gallery does not exist"}
        
    #Delete the card from the database and commit
    db.session.delete(gallery)
    db.session.commit()
    #return the gallery in the response
    return jsonify(gallery_schema.dump(gallery))
    
@gallerys.route("/<int:id>/", methods=["PUT"])
@jwt_required()
def update_gallery(id):
    if get_jwt_identity() != "admin":
        return {"error": "You don't have the permission to do this"}
    # find the gallery in the database
    gallery = Gallery.query.get(id)
    # check if the gallery exists in the database
    if not gallery:
        return {"error": "Gallery not found in the database"}
    # get the gallery from the request
    gallery_fields = gallery_schema.load(request.json)

    # modify the gallery
    gallery.name = gallery_fields["name"],
    gallery.location = gallery_fields["location"],
    gallery.phone_number = gallery_fields["phone_number"],
    gallery.open_hours = gallery_fields["open_hours"],
    gallery.description = gallery_fields["description"]

    # save changes to the database
    db.session.commit()
    return jsonify(gallery_schema.dump(gallery))


