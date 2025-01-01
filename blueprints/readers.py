from extentions import app
from models.reader import Reader, ReaderInput
from quart import Blueprint, g, render_template
from quart_schema import validate_request, validate_response

blueprint = Blueprint("readers", __name__)


@app.post("/readers/")
@validate_request(ReaderInput)
@validate_response(Reader)
async def create_reader(data: ReaderInput):
    """Create a new Reader entry"""
    result = await g.connection.fetch_one(
        """INSERT INTO readers (name)
            VALUES (:name)
            RETURNING id, name""",
        {"name": data.name},
    )

    return Reader(**result)


@app.get("/readers/")
async def get_readers():
    query = """SELECT id, name
                FROM readers"""
    readers = [Reader(**row) async for row in g.connection.iterate(query)]
    readers_data = [{"id": reader.id, "name": reader.name} for reader in readers]
    return await render_template("readers.html", readers=readers_data)


@app.get("/readers/<int:id>/")
@validate_response(Reader)
async def get_reader_by_id(id: int) -> Reader:
    """Get a reader.
    Fetch a Reader by its ID.
    """
    result = await g.connection.fetch_one(
        """SELECT id, name
            FROM readers
            WHERE id = :id""",
        {"id": id},
    )
    if result is None:
        raise Exception(f"Reader {id} not found")
    else:
        return Reader(**result)


@app.get("/readers/<string:name>/")
@validate_response(Reader)
async def get_reader_by_name(name: str) -> Reader:
    """Get a reader.
    Fetch a Reader by its name.
    """
    result = await g.connection.fetch_one(
        """SELECT id, name
            FROM readers
            WHERE name LIKE :name""",
        {"name": f"%{name}%"},
    )
    if result is None:
        raise Exception(f"Reader {name} not found")
    else:
        return Reader(**result)
