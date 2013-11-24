#from app import db

class User():
  #id = db.Column(db.Integer, primary_key = True)
  #nickname = db.Column(db.String(64), index = True, unique = True)

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)
