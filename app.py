from main_app import create_app
from dotenv import load_dotenv
import os

load_dotenv('.flaskenv')
print(os.environ.get('FLASK_ENV'))
app = create_app(os.environ.get('FLASK_ENV'))
if __name__ == '__main__':
    app.run(port="8080", host="0.0.0.0")
