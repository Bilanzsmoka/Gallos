import sqlite3

class GallosDB:
    def __init__(self, db_path="torneo_gallos.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gallos (
                id INTEGER PRIMARY KEY,
                cuerda TEXT,
                frente TEXT,
                anillo TEXT,
                placa TEXT,
                color TEXT,
                peso TEXT,
                ciudad TEXT,
                tipo TEXT,
                numeroJaula TEXT
            )
        ''')
        
        self.conn.commit()

    def create_gallo(self, *datos):
        self.cursor.execute('''
            INSERT INTO gallos (cuerda, frente, anillo, placa, color, peso, ciudad, tipo, numeroJaula)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', datos)
        self.conn.commit()

    def get_all_gallos(self):
        self.cursor.execute("SELECT * FROM gallos")
        return self.cursor.fetchall()

    def delete_gallo(self, gallo_id):
        self.cursor.execute("DELETE FROM gallos WHERE id = ?", (gallo_id,))
        self.conn.commit()

    def delete_all_gallos(self):
        self.cursor.execute("DELETE FROM gallos")
        self.conn.commit()

    def update_gallo(self, gallo_id, nuevos_datos):
        self.cursor.execute("""
            UPDATE gallos
            SET cuerda=?, frente=?, anillo=?, placa=?, color=?, peso=?, ciudad=?, tipo=?, numeroJaula=?
            WHERE id=?
        """, nuevos_datos + [gallo_id])
        self.conn.commit()

    def get_unique_cuerdas(self):
        self.cursor.execute("SELECT DISTINCT cuerda FROM gallos")
        return [row[0] for row in self.cursor.fetchall()]

    def get_gallos_by_cuerda(self, cuerda):
        self.cursor.execute("SELECT * FROM gallos WHERE cuerda = ?", (cuerda,))
        return self.cursor.fetchall()

    def get_column_names(self):
        self.cursor.execute("PRAGMA table_info(gallos);")
        return [col[1] for col in self.cursor.fetchall()]

    def close(self):
        self.conn.close()
