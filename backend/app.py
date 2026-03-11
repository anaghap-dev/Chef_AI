from flask import Flask
from routes.text_routes import text_routes

app = Flask(__name__)

# Register routes
app.register_blueprint(text_routes)


@app.route("/")
def home():
    return {"message": "ChefAI backend running"}
    

if __name__ == "__main__":
    app.run(debug=True)