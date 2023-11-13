import sqlite3

class Client:
    db = 'IoT_Dashboard.db'
    table = "client"
    conn = None
    c = None
    
    def __init__(self):
        if (not conn):
            conn = sqlite3.connect(Client.db)

        c = conn.cursor()
        Client.setup()

    def setup():
        sql = """
            CREATE TABLE IF NOT EXISTS client (
                id TEXT,
                email TEXT,
                fav_temp DECIMAL(4,1),
                fav_humid INTEGER,
                fav_light_intensity DECIMAL(6,2)
            )
        """

    def getDataById(self, user_id):
        if (not user_id):
            return
    
        sql = """SELECT * FROM client WHERE 1 {}""".format("id = {}".format(user_id))

        Client.c.execute(sql)

        return Client.c.fetchone()
    
    def update(self, user_id, data):
        if (not user_id or not data):
            return
        if (not self.getDataById(user_id)):
            return
        
        fdata = ""
        for key, val in data:
            fdata += "{} = {},".format(key, val)

        sql = """
            UPDATE {}
            SET {}
            WHERE 1 {}
        """.format(Client.table, fdata[0:-1], ("id = " + str(user_id)))

        return Client.c.execute(sql)

    def create(self, data):
        if (not data):
            return
        if (not data['id']):
            return
        
        fdata = ""
        for key, val in data:
            fdata += str(val) + ","

        sql = """
            INSERT INTO {}
            VALUES ({})
        """.format(Client.table, fdata[0:-1])

        return Client.c.execute(sql)