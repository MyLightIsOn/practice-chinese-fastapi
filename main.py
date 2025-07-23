from fastapi import FastAPI, Query
import sqlite3

app = FastAPI()
conn = sqlite3.connect("cedict.db", check_same_thread=False)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/lookup")
def lookup(text: str = Query(..., min_length=1)):
    with sqlite3.connect("cedict.db") as conn:
        cursor = conn.execute("SELECT * FROM dictionaryentry WHERE simplified LIKE ? OR traditional LIKE ?", (f"%{text}%", f"%{text}%"))
        results = cursor.fetchall()
    return [{"simplified": row[1], "traditional": row[2], "pinyin": row[3], "definition": row[4]} for row in results]