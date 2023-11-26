#File for working with sqlite
import sqlite3


class Client:
  #db = "clients.db"
  db = "clients_test.db"
  conn = None
  c = None  

  def __init__(self):
    if (not Client.conn):
      Client.conn = sqlite3.connect(Client.db)

#cursor for executing db commands
    Client.c = Client.conn.cursor()
    Client.setupDB()

  def setupDB():
    Client.c.execute("""
      CREATE TABLE IF NOT EXISTS clients_test (
        id TEXT,
        username TEXT,
        email TEXT,
        fav_temp DECIMAL(4,1),
        fav_humid INTEGER,
        fav_light_intensity DECIMAL(6,2)
      )
      """)    

  def getClient(self, id):
    sql = "SELECT email, username, fav_temp, fav_humid, fav_light_intensity FROM clients_test WHERE id = :id;"
    Client.c.execute(sql, {"id": id})

    return Client.c.fetchone()

  def create(self, data):
    sql = """
      INSERT INTO clients_test VALUES (:id, :username, :email, :fav_temp, :fav_humid, :fav_light_intensity)
    """

    res = Client.c.execute(sql, data)
    Client.conn.commit()
    return res

  def update(self, id, data):
    sql = """
      UPDATE clients_test
      SET 
        id = :id,
        email = :email,
        username = :username,
        fav_temp = :fav_temp,
        fav_humid = :fav_humid,
        fav_light_intensity = :fav_light_intensity
      WHERE id = "{}"
    """.format(id)

    return Client.c.execute(sql, data)
