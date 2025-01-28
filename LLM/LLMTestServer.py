import dotenv
import os
import Flask

dotenv.load_dotenv()
PORT_NUMBER = os.getenv("PORT_NUMBER")

app = Flask(__name__)