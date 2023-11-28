#File for working with sqlite
import sqlite3


class Client:
  #db = "clients.db"
  db = "clients_test.db"

  default_fav_temp = 24
  default_fav_humid = 40
  default_fav_lightInt = 400

  def __init__(self):
    conn, c = self.connectDB()
    #cursor for executing db commands
    self.setupDB()

    c.close
    conn.close


  def connectDB(self):
    conn = sqlite3.connect(Client.db)
    c = conn.cursor()
    return conn, c


  def setupDB(self):
    conn, c = self.connectDB()

    c.execute("""
      CREATE TABLE IF NOT EXISTS clients_test (
        id TEXT,
        username TEXT,
        email TEXT,
        fav_temp DECIMAL(4,1),
        fav_humid INTEGER,
        fav_light_intensity DECIMAL(6,2)
      )
      """)
    
    c.close
    conn.close

  def login(self, id):
    cols, data = self.getClient(id)
    
    if (not data):
      self.create({
        'id': id,
        'username': id,
        'email': "N/A",
        'fav_temp': Client.default_fav_temp,
        'fav_humid': Client.default_fav_humid,
        'fav_light_intensity': Client.default_fav_lightInt
      })
    cols, data = self.getClient(id)
    
    return self.convert_data_to_dict(cols, data)


  def getClient(self, id):
    conn, c = self.connectDB()

    sql = "SELECT id, username, email, fav_temp, fav_humid, fav_light_intensity FROM clients_test WHERE id = :id;"
    
    c.execute(sql, {"id": id})
    
    data = c.fetchone()
    cols = c.description

    c.close
    conn.close

    return cols, data

  def convert_data_to_dict(self, cols, data):
    res = {}
    for i in range(len(data)):
      res[cols[i][0]] = data[i]
    
    return res

  def create(self, data):
    conn, c = self.connectDB()

    sql = """
      INSERT INTO clients_test VALUES (:id, :username, :email, :fav_temp, :fav_humid, :fav_light_intensity)
    """

    res = c.execute(sql, data)

    conn.commit()

    c.close
    conn.close

    return res

  def update(self, id, data):
    conn, c = self.connectDB()

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

    res = c.execute(sql, data)
    c.commit()

    c.close
    conn.close

    return res