from flask import Flask
from flask_cors import CORS
from routes.text_routes import text_routes

app = Flask(__name__)
CORS(app)

# Register blueprint with prefix
app.register_blueprint(text_routes, url_prefix="")  # or url_prefix="/api" if you want /api/search/text

@app.route("/")
def home():
    return {"message": "ChefAI backend running"}

if __name__ == "__main__":
    app.run(debug=True)