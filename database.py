import aiosqlite
DB_PATH = "korshun_tickets.db"
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                category_id INTEGER,
                log_channel_id INTEGER,
                support_role_id INTEGER,
                open_role_id INTEGER,
                close_role_id INTEGER,
                panel_channel_id INTEGER,
                panel_message_id INTEGER,
                panel_title TEXT DEFAULT '🎫 Поддержка',
                panel_description TEXT DEFAULT 'Нажмите кнопку ниже, чтобы создать тикет.',
                panel_color TEXT DEFAULT '#5865F2',
                panel_image TEXT,
                panel_thumbnail TEXT,
                ticket_counter INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                name TEXT,
                emoji TEXT,
                description TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER UNIQUE,
                user_id INTEGER,
                category TEXT,
                subject TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
