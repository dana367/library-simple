from quart import Quart
from quart_db import QuartDB
from quart_schema import QuartSchema

app = Quart(__name__)
QuartSchema(app)
db = QuartDB(app, url="sqlite:///database.db")
