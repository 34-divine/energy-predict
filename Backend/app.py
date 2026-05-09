from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.units_routes import units_bp
from routes.predict_routes import predict_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(units_bp, url_prefix="/api/units")
app.register_blueprint(predict_bp, url_prefix="/api/predict")

@app.route("/")
def home():
    return {"message": "Energy Prediction API is running"}

if __name__ == "__main__":
    app.run(debug=True)