from wtforms import Form, StringField, validators


class CreateForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=255)])
    ip = StringField('Ip', [validators.IPAddress(ipv4=True, ipv6=False)])
