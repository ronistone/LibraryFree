from flask import g, jsonify
from flask_restful import Resource, reqparse
from app import app, db, auth, api
from app.models.tables import Book, Book_loan, Book_return
from sqlalchemy.sql import and_, or_


class BooksApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True,
                                   location='json')
        self.reqparse.add_argument("synopsis", type=str, location='json')
        self.reqparse.add_argument("author", type=str, required=True,
                                   location='json')
        self.reqparse.add_argument("publisher", type=str, required=True,
                                   location='json')
        self.reqparse.add_argument("edition", type=int, location='json')
        self.reqparse.add_argument("year", type=int, location='json')
        self.reqparse.add_argument("language", type=str, location='json')
        self.reqparse.add_argument("genre", type=str, location='json')
        super(BooksApi, self).__init__()

    def get(self):
        # This parameters are specific to the GET method
        # because they are not mandatory
        search_reqparse = reqparse.RequestParser()
        search_reqparse.add_argument("title", type=str, location='json')
        search_reqparse.add_argument("author", type=str, location='json')
        search_reqparse.add_argument("publisher", type=str, location='json')
        search_reqparse.add_argument("genre", type=str, location='json')

        # retrieving the values
        args = search_reqparse.parse_args()

        filters_list = []

        if args['title']:
            filters_list.append(
                Book.title.ilike("%{0}%".format(args['title']))
            )

        if args['author']:
            filters_list.append(
                Book.author.ilike("%{0}%".format(args['author']))
            )

        if args['publisher']:
            filters_list.append(
                Book.publisher.ilike("%{0}%".format(args['publisher']))
            )

        if args['genre']:
            filters_list.append(
                Book.genre == args['genre']
            )

        filtering = and_(*filters_list)

        books = Book.query.filter(filtering).all()

        return {'data': [book.serialize for book in books]}, 200

    def post(self):
        args = self.reqparse.parse_args()
        book = Book(**args)
        db.session.add(book)
        db.session.commit()
        return {'data': book.serialize}, 200


class ModifyBooksApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, location='json')
        self.reqparse.add_argument("synopsis", type=str, location='json')
        self.reqparse.add_argument("author", type=str, location='json')
        self.reqparse.add_argument("publisher", type=str, location='json')
        self.reqparse.add_argument("edition", type=int, location='json')
        self.reqparse.add_argument("year", type=int, location='json')
        self.reqparse.add_argument("language", type=str, location='json')
        self.reqparse.add_argument("genre", type=str, location='json')
        super(ModifyBooksApi, self).__init__()

    def get(self, id):
        book = Book.query.get_or_404(id)
        return {'data': book.serialize}, 200

    def put(self, id):
        book = Book.query.get_or_404(id)
        args = self.reqparse.parse_args()

        for key, value in args.items():
            if value is not None:
                setattr(book, key, value)

        db.session.commit()
        return {'data': book.serialize}, 200

    def delete(self, id):
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return 204

class BooksAvailabilityApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("book_id", type=int, required=True,
                                   location='json')
        self.reqparse.add_argument("user_id", type=int, required=True,
                                   location='json')
        super(BooksAvailabilityApi, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        query = Book_loan.query.filter_by(book_id=args['book_id'],
                                                  user_id=args['user_id']).first()
        if not query:
            return {'data': {'message': 'Erro inesperado!'}}, 500
        else:
            return {'data': query.loan_status},200

class ReturnApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("book_id", type=int, required=True,
                                   location='json')
        self.reqparse.add_argument("user_id", type=int, required=True,
                                   location='json')
        self.reqparse.add_argument("owner_id", type=int, required=True,
                                   location='json')
        self.reqparse.add_argument("confirmed_by", type=str,
                                   location='json')
        super(ReturnApi, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        loan_record = Book_loan.query.filter_by(book_id=args['book_id'],
                                                  owner_id=args['owner_id'],
                                                  user_id= args['user_id']).first()
        return_record = Book_return.query.filter_by(book_loan_id =
                                                    loan_record.id).first()
        if not (return_record):
            return_record = Book_return(book_loan_id = loan_record.id,
                                        returned_date = datetime.now())
            db.session.add(book_return)

        if(args['confirmed_by']=='owner'):
            return_record.owner_confirmation=True
        elif(args['confirmed_by']=='user'):
            return_record.user_confirmation=True
        else:
            abort(400)
        db.session.commit()

        return 204

    def get(self):
        args = self.reqparse.parse_args()
        loan_record_search = Book_loan.query.filter_by(book_id=args['book_id'],
                                                  owner_id=args['owner_id'],
                                                  user_id= args['user_id']).first()
        return_record_search = Book_return.query.filter_by(book_loan_id =
                                                    loan_record.id).first()

        return {'data': [return_record_search.serialize]}, 200


api.add_resource(BooksApi, '/api/v1/books', endpoint='books')
api.add_resource(ModifyBooksApi, '/api/v1/books/<int:id>', endpoint='modify_books')
api.add_resource(BooksAvailabilityApi, '/api/v1/books/availability', endpoint='books_availability')
api.add_resource(ReturnApi, '/api/v1/books/return', endpoint='return')