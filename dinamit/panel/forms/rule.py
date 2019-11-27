from wtforms import Form, StringField, validators
from dinamit.core.constants import DomainAction
import re


class CreateForm(Form):
    source = StringField('Source', [validators.Length(min=4, max=255)])
    destination = StringField('Destination', [validators.Length(min=4, max=255)])
    action = StringField('Action', [validators.Length(min=4, max=5)])

    def validate(self):
        try:
            DomainAction[self.action.data]
        except KeyError:
            return False

        try:
            re.compile(self.destination.data, re.IGNORECASE)
        except Exception:
            return False

        return True
