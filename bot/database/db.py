import aiosqlite
import os
from config import DATABASE_PATH

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                article TEXT,
                photo_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                products TEXT NOT NULL,  -- JSON list of product IDs
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.commit()


# ─── Users ─────────────────────────────────────────────────────────────────────

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def create_user(telegram_id: int, name: str, phone: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, name, phone) VALUES (?, ?, ?)",
            (telegram_id, name, phone),
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users ORDER BY registered_at DESC"
        ) as cursor:
            return await cursor.fetchall()


# ─── Products ──────────────────────────────────────────────────────────────────

async def get_all_products():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products ORDER BY id") as cursor:
            return await cursor.fetchall()


async def get_product(product_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ) as cursor:
            return await cursor.fetchone()


async def create_product(name: str, description: str = None, price: float = None,
                          article: str = None, photo_path: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO products (name, description, price, article, photo_path) VALUES (?, ?, ?, ?, ?)",
            (name, description, price, article, photo_path),
        )
        await db.commit()
        return cursor.lastrowid


async def update_product(product_id: int, name: str, description: str = None,
                          price: float = None, article: str = None, photo_path: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """UPDATE products SET name=?, description=?, price=?, article=?, photo_path=?
               WHERE id=?""",
            (name, description, price, article, photo_path, product_id),
        )
        await db.commit()


async def delete_product(product_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()


async def bulk_create_products(products: list[dict]):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executemany(
            "INSERT INTO products (name, description, price, article) VALUES (?, ?, ?, ?)",
            [(p.get("name"), p.get("description"), p.get("price"), p.get("article")) for p in products],
        )
        await db.commit()


# ─── Orders ────────────────────────────────────────────────────────────────────

async def create_order(user_id: int, product_ids: list[int]):
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, products) VALUES (?, ?)",
            (user_id, json.dumps(product_ids)),
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_orders():
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT o.id, o.products, o.created_at,
                   u.name AS user_name, u.phone, u.telegram_id
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
        """) as cursor:
            rows = await cursor.fetchall()
    return rows
