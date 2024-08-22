from quart_wtf import QuartForm
from quart_babel import gettext
from wtforms import StringField, HiddenField, BooleanField, Field
from wtforms import SelectField
from wtforms.validators import DataRequired, Email
from wtforms.widgets import TextInput


class CommaSeparatedListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ",".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if (
            valuelist == [""] or valuelist == [None] or valuelist == ["None"]
        ):  # An empty string from the client is equal to an empty array
            self.data = []
        elif len(valuelist):
            self.data = [x.strip() for x in valuelist[0].split(",")]
        else:
            # No data was provided by client, store `None` so we know not to process this field
            self.data = None


BooleanField.false_values = {False, "false", "", "False"}


class UserForm(QuartForm):
    class Meta:
        csrf = False

    user_types = [
        ("administrator", gettext("Administrator")),
        ("public", gettext("Public")),
        ("internal", gettext("Internal")),
        ("account_management", gettext("Account Management")),
        ("company_admin", gettext("Company Admin")),
    ]

    _id = HiddenField("Id")
    first_name = StringField(gettext("First Name"), validators=[DataRequired()])
    last_name = StringField(gettext("Last Name"), validators=[DataRequired()])
    email = StringField(gettext("Email"), validators=[DataRequired(), Email()])
    phone = StringField(gettext("Telephone"), validators=[])
    mobile = StringField(gettext("Mobile"), validators=[])
    role = StringField(gettext("Role"), validators=[])
    user_type = SelectField(gettext("User Type"), choices=user_types)
    company = StringField(gettext("Company"), validators=[])
    is_validated = BooleanField(gettext("Email Validated"), validators=[])
    is_enabled = BooleanField(gettext("Account Enabled"), default=True, validators=[])
    is_approved = BooleanField(gettext("Account Approved"), validators=[])
    expiry_alert = BooleanField(gettext("Company Expiry Alert"), validators=[])
    receive_email = BooleanField(gettext("Receive Email Notifications"), default=True, validators=[])
    receive_app_notifications = BooleanField(gettext("Receive App Notifications"), default=True, validators=[])
    locale = StringField(gettext("Locale"))
    manage_company_topics = BooleanField(gettext("Manage Company Topics"), validators=[])

    sections = CommaSeparatedListField(gettext("Sections"), validators=[])
    products = CommaSeparatedListField(gettext("Products"), validators=[])
