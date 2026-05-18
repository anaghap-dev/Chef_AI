import os
from flask import Flask
from flask_cors import CORS
from routes.text_routes import text_routes
from routes.image_routes import image_bp
from routes.Subs import subs_routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprint with prefix
app.register_blueprint(text_routes, url_prefix="")
app.register_blueprint(image_bp, url_prefix="")
app.register_blueprint(subs_routes, url_prefix="")

@app.route("/")
def home():
    return {"message": "ChefAI backend running"}

if __name__ == "__main__":
    app.run(debug=True)