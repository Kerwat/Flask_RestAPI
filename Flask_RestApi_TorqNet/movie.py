import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required


class Movie(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("show_id", type=int, required=True, help="This field cannot be left empty")
    parser.add_argument("type", type=str, required=True, help="This field cannot be left empty")
    parser.add_argument("country", type=str, required=True, help="This field cannot be left empty")
    parser.add_argument("release_year", type=int, required=True, help="This field cannot be left empty")
    parser.add_argument("rating", type=str, required=True, help="This field cannot be left empty")
    parser.add_argument("duration", type=str, required=True, help="This field cannot be left empty")
    parser.add_argument("listed_in", type=str, required=True, help="This field cannot be left empty")

    @classmethod
    def find_by_name(cls, title):
        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        query = "SELECT * FROM shows_and_movies WHERE title=?"
        result = cursor.execute(query, (title,))
        row = result.fetchone()
        connection.close()

        if row:
            return {"movie": {"type": row[1], "title": row[2], "country": row[3], "release_year": row[4], "rating": row[5], "duration": row[6], "listed_in": row[7]}}

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        query = "INSERT INTO shows_and_movies VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (item["show_id"], item["type"], item["title"], item["country"], item["release_year"], item["rating"], item["duration"], item["listed_in"]))

        connection.commit()
        connection.close()


    @classmethod
    def update(cls, item): # I'm using "listed_in" here as an example
        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        query = "UPDATE shows_and_movies SET listed_in=? WHERE title=?"
        cursor.execute(query, (item["listed_in"], item["title"]))

        connection.commit()
        connection.close()


    def get(self, title):
        item = Movie.find_by_name(title)
        if item:
            return item
        return {"messege": "Item not found."}, 404


    def post(self, title):
        if Movie.find_by_name(title):
            return {"messege": f"An movie with title {title} already exists"}, 400 # 400 means bad request

        # data = request.get_json()
        data = Movie.parser.parse_args()
        item = {"show_id": data["show_id"], "type": data["type"], "title": title, "country": data["country"], "release_year": data["release_year"], "rating": data["rating"], "duration": data["duration"], "listed_in": data["listed_in"]}
        
        try:
            Movie.insert(item)
        except:
            return {"messege": "An error occurred inserting the item."}, 500 # Internal Server Error

        # we always have to return JSON "No objects or any data type"
        return item, 201


    def put(self, title):
        # data = request.get_json()
        data = Movie.parser.parse_args()
        item = Movie.find_by_name(title)

        update_item = {"show_id": data["show_id"], "type": data["type"], "title": title, "country": data["country"], "release_year": data["release_year"], "rating": data["rating"], "duration": data["duration"], "listed_in": data["listed_in"]}

        if item is None:
            try:
                Movie.insert(update_item)
            except:
                return {"messege": "An error occurred inserting the item."}, 500
        else:
            try: # using "listed_in" to update as an example
                Movie.update(update_item)
            except:
                return {"messege": "An error occured updating the item."}, 500

        return update_item


    def delete(self, title):

        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        query = "DELETE FROM shows_and_movies WHERE title=?"
        cursor.execute(query, (title,))

        connection.commit()
        connection.close()

        return {"messege": "Item deleted"}



class MoviesList(Resource):
    def get(self):
        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        query = "SELECT * FROM shows_and_movies WHERE type='Movie' ORDER BY release_year LIMIT 20"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({"show_id": row[0], "type": row[1], "title": row[2], "country": row[3], "release_year": row[4], "rating": row[5], "duration": row[6], "listed_in": row[7]})

        connection.close()

        return {"movies": items}


class MoviesInfo(Resource):
    @jwt_required()
    def get(self, info):
        connection = sqlite3.connect("netflix_titles.db")
        cursor = connection.cursor()

        if info == "count":
            query_count = "SELECT COUNT(type) FROM shows_and_movies WHERE type='Movie'"
            result = cursor.execute(query_count)
            result = result.fetchall()
            connection.close()
            return {"number of movies": result[0][0]}, 200
        elif info == "newest":
            query_max = "SELECT MAX(release_year) FROM shows_and_movies WHERE type='Movie'"
            result = cursor.execute(query_max)
            result = result.fetchall()
            connection.close()
            return {"newest movie year is": result[0][0]}, 200
        elif info == "oldest":
            query_min = "SELECT MIN(release_year) FROM shows_and_movies WHERE type='Movie'"
            result = cursor.execute(query_min)
            result = result.fetchall()
            connection.close()
            return {"oldest movie year is": result[0][0]}, 200
        else:
            return {"ERROR Messege": "Please choose: 'count', 'oldest', or 'newest' in the link above"}, 404