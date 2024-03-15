import os
import time
import sqlite3


class ProductDatabaseOperator:
    '''
    Operate database for product information.
    '''
    def __init__(self, database_path: str="./data/products.db"):
        self.database_path = database_path
        self.create_database()

    def create_database(self):
        if os.path.exists(self.database_path):
            print("[INFO] Database exists. Connect to the existing database.")
            pass
        else:
            conn = sqlite3.connect(database=self.database_path)
            curs = conn.cursor()
            curs.execute("""CREATE TABLE PRODUCTS(
                        ID            INTEGER PRIMARY KEY AUTOINCREMENT,
                        POST_TIME     INT                  NOT NULL,
                        NAME          TEXT                 NOT NULL,
                        DESCRIPTION   TEXT                 NOT NULL,
                        SELLER        TEXT                 NOT NULL,
                        PRICE         REAL                 NOT NULL,
                        MESSAGE       TEXT                 NOT NULL,
                        IMG           TEXT                 NOT NULL,
                        STATUS        TEXT                 NOT NULL
            );""")
            conn.commit()
            conn.close()
            print("[INFO] Create new database. And connect to the new database.")


    def add_entry(self, name: str, seller: str, price: float, description: str, message: str, img: str=None):
        """
        Add an product entry to the database.

        Parameters:
        name (str): name of the product.
        seller (str): seller of the product.
        price (float): price set by posting of the product.
        description (str): message left by the seller.
        img (str): path to the product image.
        """
        # Get timestamp.
        post_time = int(time.time())

        conn = sqlite3.connect(database=self.database_path)
        curs = conn.cursor()
        curs.execute("""INSERT INTO PRODUCTS 
                     (POST_TIME, NAME, DESCRIPTION, SELLER, PRICE, MESSAGE, IMG, STATUS)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                     (post_time, name, description, seller, price, message, img, "available"))
        conn.commit()
        conn.close()

    def change_entry_status(self, id: int, new_status: str):
        """
        Disable one specific product entry.

        Parameters:
        id (int): ID of the entry in database.
        """
        conn = sqlite3.connect(database=self.database_path)
        curs = conn.cursor()
        curs.execute(f"""UPDATE PRODUCTS
                     SET STATUS = '{new_status}'
                     WHERE ID = {id}""")
        conn.commit()


    def get_all(self, status: str="available", seller: str=None) -> list:
        conn = sqlite3.connect(database=self.database_path)
        curs = conn.cursor()
        if seller is None:
            curs.execute(f"SELECT * FROM PRODUCTS WHERE STATUS = '{status}'")
        else:
            curs.execute(f"SELECT * FROM PRODUCTS WHERE STATUS = '{status}' AND SELLER = '{seller}'")
        columns = [column[0] for column in curs.description]
        result = []
        for row in curs.fetchall():
            result.append(dict(zip(columns, row)))
        conn.close()
        return result

