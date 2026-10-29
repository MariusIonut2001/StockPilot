
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "stockpilot.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():

    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS gestiuni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod TEXT NOT NULL UNIQUE,
                denumire TEXT NOT NULL,
                activa INTEGER NOT NULL DEFAULT 1
                    CHECK (activa IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS unitati_masura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                denumire TEXT NOT NULL UNIQUE,
                activa INTEGER NOT NULL DEFAULT 1
                    CHECK (activa IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS materiale (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gestiune_id INTEGER NOT NULL,
                cod TEXT,
                denumire TEXT NOT NULL,
                unitate_id INTEGER NOT NULL,
                activ INTEGER NOT NULL DEFAULT 1
                    CHECK (activ IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (gestiune_id)
                    REFERENCES gestiuni(id),
                FOREIGN KEY (unitate_id)
                    REFERENCES unitati_masura(id)
            );

            CREATE TABLE IF NOT EXISTS destinatari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_atelier TEXT NOT NULL UNIQUE,
                sef_atelier TEXT NOT NULL,
                activ INTEGER NOT NULL DEFAULT 1
                    CHECK (activ IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS miscari_stoc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                tip TEXT NOT NULL CHECK (
                    tip IN (
                        'STOC_INITIAL',
                        'INTRARE',
                        'IESIRE',
                        'AJUSTARE',
                        'STORNARE'
                    )
                ),
                cantitate REAL NOT NULL CHECK (cantitate > 0),
                sens INTEGER NOT NULL CHECK (sens IN (-1, 1)),
                data_operatiunii TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                destinatar_id INTEGER,
                cod_atelier_snapshot TEXT,
                sef_atelier_snapshot TEXT,
                observatii TEXT,
                motiv TEXT,
                miscare_referinta_id INTEGER,
                FOREIGN KEY (material_id) REFERENCES materiale(id),
                FOREIGN KEY (destinatar_id) REFERENCES destinatari(id),
                FOREIGN KEY (miscare_referinta_id)
                    REFERENCES miscari_stoc(id),
                UNIQUE (miscare_referinta_id)
            );

            CREATE TABLE IF NOT EXISTS inventarieri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                data_inventarierii TEXT NOT NULL,
                cantitate_scriptica REAL NOT NULL,
                cantitate_faptica REAL NOT NULL
                    CHECK (cantitate_faptica >= 0),
                diferenta REAL NOT NULL,
                observatii TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (material_id) REFERENCES materiale(id)
            );

            CREATE INDEX IF NOT EXISTS idx_materiale_gestiune
                ON materiale(gestiune_id);

            CREATE INDEX IF NOT EXISTS idx_materiale_denumire
                ON materiale(denumire);

            CREATE INDEX IF NOT EXISTS idx_miscari_material_data
                ON miscari_stoc(material_id, data_operatiunii);

            CREATE INDEX IF NOT EXISTS idx_inventarieri_material_data
                ON inventarieri(material_id, data_inventarierii);
        """)

def verify_tables():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        print("Tabele existente:")
        for row in rows:
            print(f"- {row['name']}")


if __name__ == "__main__":
    init_db()
    verify_tables()
