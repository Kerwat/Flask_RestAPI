from flask import Flask
from flask_restful import Api
from flask_jwt import JWT


from security import authenticate, identity
from user import UserRegister
from show import Show, ShowsList, ShowsInfo
from movie import Movie, MoviesList, MoviesInfo

app = Flask(__name__)
app.secret_key = "keras"
api = Api(app)

jwt = JWT(app, authenticate, identity) # it will create an "/auth" endpoint 


api.add_resource(ShowsList, "/shows")
api.add_resource(MoviesList, "/movies")
api.add_resource(Show, "/show/<string:title>")
api.add_resource(Movie, "/movie/<string:title>")
api.add_resource(MoviesInfo, "/movies_info/<string:info>")
api.add_resource(ShowsInfo, "/shows_info/<string:info>")
api.add_resource(UserRegister, "/register")


if __name__ == "__main__":
    app.run(port=5000, debug=True)