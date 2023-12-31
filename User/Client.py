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
    return

  def login(self, id):
    data = self.getClient(id)
    
    if (not data):
      self.create({
        'id': id,
        'username': id,
        'email': "N/A",
        'fav_temp': Client.default_fav_temp,
        'fav_humid': Client.default_fav_humid,
        'fav_light_intensity': Client.default_fav_lightInt
      })
    data = self.getClient(id)
    print(data)
    
    return data


  def getClient(self, id):
    conn, c = self.connectDB()

    sql = "SELECT id, username, email, fav_temp, fav_humid, fav_light_intensity FROM clients_test WHERE id = :id;"
    
    c.execute(sql, {"id": id})
    
    data = c.fetchone()
    cols = c.description

    c.close
    conn.close

    return self.convert_data_to_dict(cols, data)

  def convert_data_to_dict(self, cols, data):
    if not cols or not data:
      return None
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
        email = :email,
        username = :username,
        fav_temp = :fav_temp,
        fav_humid = :fav_humid,
        fav_light_intensity = :fav_light_intensity
      WHERE id = "{}"
    """.format(id)

    res = c.execute(sql, data)
    conn.commit()
    print(self.getClient(id))
    c.close
    conn.close
    data['id'] = id
    return self.check_updated(id, data)
  
  def check_updated(self, id, data):
    fromDB = self.getClient(id)

    if (fromDB['id'] != data['id']):
      return 0
    if (fromDB['email'] != data['email']):
      return 0
    if (fromDB['username'] != data['username']):
      return 0
    if (fromDB['fav_temp'] != data['fav_temp']):
      return 0
    if (fromDB['fav_humid'] != data['fav_humid']):
      return 0
    if (fromDB['fav_light_intensity'] != data['fav_light_intensity']):
      return 0
    return 1
    