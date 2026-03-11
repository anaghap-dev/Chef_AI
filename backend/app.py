from flask import Flask
from routes.text_routes import text_bp
from routes.image_routes import image_bp
from routes.voice_routes import voice_bp

app = Flask(__name__)

app.register_blueprint(text_bp)
app.register_blueprint(image_bp)
app.register_blueprint(voice_bp)

if __name__ == "__main__":
    app.run(debug=True)