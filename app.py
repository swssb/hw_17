# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

    def __repr__(self):
        return self.title


class MovieSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    director_id = fields.Integer()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        arg_director = request.args.get('director_id')
        arg_genre = request.args.get('genre_id')
        if arg_director:
            movies_with_director = db.session.query(Movie).filter(Movie.director_id == arg_director).all()
            return movies_schema.dump(movies_with_director)
        elif arg_genre:
            movies_with_genre = db.session.query(Movie).filter(Movie.genre_id == arg_genre).all()
            return movies_schema.dump(movies_with_genre)
        elif arg_genre and arg_director:
            movies_select = db.session.query(Movie).filter(Movie.genre_id == arg_genre,
                                                           Movie.director_id == arg_director).all()
            return movies_schema.dump(movies_select)
        movies = db.session.query(Movie).all()
        if not movies:
            return 'Movies database is empty', 404
        return movies_schema.dump(movies), 200

    def post(self):

        req = request.json
        new_movie = Movie(**req)
        db.session.add(new_movie)
        db.session.commit()
        print(req)
        if req is None:
            return 'no data to post', 404
        return f'movie {new_movie.title} is added', 201


@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return 'invalid id', 404
        return movie_schema.dump(movie), 200

    def put(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return 'invalid id', 404
        req = request.json
        if not req:
            return 'no data to change', 404
        movie.title = req.get('title')
        movie.description = req.get('description')
        movie.trailer = req.get('trailer')
        movie.year = req.get('year')
        movie.rating = req.get('rating')
        movie.genre_id = req.get('genre_id')
        movie.director_id = req.get('director_id')
        db.session.add(movie)
        db.session.commit()
        return f'movie {movie.title} is changed', 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return 'invalid id', 404
        db.session.delete(movie)
        db.session.commit()
        return f'movie {movie.title} is deleted', 204


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        if not directors:
            return 'Directors database is empty', 404
        return directors_schema.dump(directors), 200

    def post(self):
        req = request.json
        new_director = Director(**req)
        db.session.add(new_director)
        db.session.commit()
        if not req:
            return 'no data to post', 404
        return f'director {new_director.name} is added', 201


@directors_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        if not director:
            return 'invalid id', 404
        return director_schema.dump(director), 200

    def put(self, did):
        director = Director.query.get(did)
        if not director:
            return 'invalid id', 404
        req = request.json
        if not req:
            return 'No data to post', 404
        director.name = req.get('name')
        db.session.add(director)
        db.session.commit()
        return f'director {director.name} is changed', 204

    def delete(self, did):
        director = Director.query.get(did)
        if not director:
            return 'invalid id', 404
        db.session.delete(director)
        db.session.commit()
        return f'director {director.name} is deleted', 204


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        if not genres:
            return 'Genres database is empty', 404
        return genres_schema.dump(genres), 200

    def post(self):
        req = request.json
        if not req:
            return 'No data to add', 404
        new_genre = Genre(**req)
        db.session.add(new_genre)
        db.session.commit()
        return f'genre {new_genre.name} is added', 201


@genres_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return 'invalid id ', 404
        return genre_schema.dump(genre), 200

    def put(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return 'invalid id', 404
        req = request.json
        if not req:
            return 'no data to add', 404
        genre.name = req.get('name')
        db.session.add(genre)
        db.session.commit()
        return f'genre {genre.name} is changed', 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return 'invalid id', 404
        db.session.delete(genre)
        db.session.commit()
        return f'genre {genre.name} is deleted', 204


if __name__ == '__main__':
    app.run(debug=True)
