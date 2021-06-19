from flask import Flask
from flask_restful import Resource, Api, reqparse
from anime_scraper import AnimeScraper, SearchResultNotFound
from os import environ

app = Flask(__name__)
api = Api(app)

global scraper
scraper = AnimeScraper()

class SearchResults(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('animeName', required=True)
        parser.add_argument('unformatted', required=False, default=False)

        args = parser.parse_args()

        try:
            results = scraper.get_search_results(args["animeName"], unformatted=args["unformatted"])
            image_results = scraper.get_image_results(args["animeName"])
        except SearchResultNotFound:
            return {
                "message": f"There is no anime with the name '{args['animeName']}'"
            }, 401

        finalResults = {
            "results": results,
            "images": image_results
        }

        return finalResults, 200

class AnimeInfo(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('animeName', required=True)
        parser.add_argument('searchIndex', required=True)

        args = parser.parse_args()

        try:
            results = scraper.get_anime_info(args["animeName"], int(args["searchIndex"]))
        except SearchResultNotFound:
            return {
                "message": f"There is no anime with the name '{args['animeName']}'"
            }, 401

        finalResults = {
            "info": results
        }

        return finalResults, 200

class Episode(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('animeName', required=True)
        parser.add_argument('searchIndex', required=True)
        parser.add_argument('epNum', required=False, default=0)

        args = parser.parse_args()

        try:
            result = scraper.get_video_link(args["animeName"], args["epNum"], args["searchIndex"])
        except SearchResultNotFound:
            return {
                "message": f"There is no anime with the name '{args['animeName']}'"
            }, 401

        finalResults = {
            "episodeLink": result
        }

        return finalResults, 20
        
        

        
        

if __name__ == '__main__':
    api.add_resource(SearchResults, '/search')
    api.add_resource(AnimeInfo, '/anime')
    app.run(port=environ.get('PORT'))

