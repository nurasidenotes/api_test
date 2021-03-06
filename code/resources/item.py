from flask import Flask
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank."
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id."
    )  

    @jwt_required()
    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'An error occured searching the database.'}, 500
        
        if item:
            return item.json()
        return {'message': 'Item not found.'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'Item {} already exists.'.format(name)}, 400 #something was wrong with request (bad request)
        
        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured inserting the item.'}, 500 #internal server error
        
        return {'message': 'Your item was created.', 'item': item.json()}, 201
    
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message': 'item deleted.'}, 201
    
    def put(self, name):
        data = Item.parser.parse_args()
        
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
            item.save_to_db()
            return {'message': 'Item has been added.', 'item': item.json()}, 201
        else:
            item.price = data['price']
            item.save_to_db()
            return {'message': 'Item has been updated.', 'item': item.json()}, 201


class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.query.all()]}