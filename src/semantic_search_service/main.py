import asyncio
import sys

from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool

app = FastAPI()

@app.get("/")
def status():
    return {"status": "ok"}

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def main():
        conn_info = "dbname=vectordb host=localhost user=admin password=admin"
        pool = AsyncConnectionPool(conninfo=conn_info, open=False, timeout=5)
        await pool.open()
        async with pool.connection() as conn:
            res = await conn.status
            print(res)
        await pool.close()

    asyncio.run(main())
