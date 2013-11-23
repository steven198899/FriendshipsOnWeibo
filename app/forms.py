from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class SearchForm(Form):
 	searchName = TextField('searchName', validators = [Required()])
 	# remember_me = BooleanField('remember_me', default = False)