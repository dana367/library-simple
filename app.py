from quart import Quart

app = Quart(__name__)


@app.get("/")
async def hello():
    return "Hello, World!"
