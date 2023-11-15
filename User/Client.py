import sqlite3


class Client:
  db = "clients.db"
  conn = None
  c = None

  def __init__(self):
    if (not Client.conn):
      Client.conn = sqlite3.connect(Client.db)

    Client.c = Client.conn.cursor()
    Client.setupDB()

  def setupDB():
    Client.c.execute("""
      CREATE TABLE IF NOT EXISTS clients (
        id TEXT,
        email TEXT,
        fav_temp DECIMAL(4,1),
        fav_humid INTEGER,
        fav_light_intensity DECIMAL(6,2)
      )
      """)

  def getClient(self, id):
    sql = "SELECT email, fav_temp, fav_humid, fav_light_intensity FROM clients WHERE id = :id;"
    Client.c.execute(sql, {"id": id})

    return Client.c.fetchone()

  def create(self, data):
    sql = """
      INSERT INTO clients VALUES (:id, :email, :fav_temp, :fav_humid, :fav_light_intensity)
    """

    res = Client.c.execute(sql, data)
    Client.conn.commit()
    return res

  def update(self, id, data):
    sql = """
      UPDATE clients
      SET 
        email = :email,
        fav_temp = :fav_temp,
        fav_humid = :fav_humid,
        fav_light_intensity = :fav_light_intensity
      WHERE id = "{}"
    """.format(id)

    return Client.c.execute(sql, data)
