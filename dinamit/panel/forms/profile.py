from wtforms import Form, StringField, validators


class UpdateForm(Form):
    first_name = StringField('First Name', [validators.Length(min=4, max=255)])
    last_name = StringField('Last Name', [validators.Length(min=4, max=255)])
    email = StringField('Email', [validators.Email()])
