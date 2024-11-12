from flask_wtf import FlaskForm, RecaptchaField
from flask_babel import lazy_gettext
from wtforms import StringField, PasswordField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    company_sizes = [("0-10", "0-10"), ("11-100", "11-100"), (">100", ">100")]
    occupations = [
        ("Editor", lazy_gettext("Editor")),
        ("Journalist", lazy_gettext("Journalist")),
        ("Sales", lazy_gettext("Sales")),
        ("CTO", lazy_gettext("CTO")),
        ("CEO", lazy_gettext("CEO")),
        ("Other", lazy_gettext("Other")),
    ]

    email = StringField(lazy_gettext("Your email"), validators=[DataRequired(), Length(1, 128), Email()])
    first_name = StringField(lazy_gettext("Your First Name"), validators=[DataRequired(), Length(1, 128)])
    last_name = StringField(lazy_gettext("Your Last Name"), validators=[DataRequired(), Length(1, 128)])
    phone = StringField(lazy_gettext("Your telephone number"), validators=[DataRequired()])
    company = StringField(lazy_gettext("Your company"), validators=[DataRequired()])
    country = SelectField(lazy_gettext("Your country"), validators=[DataRequired()], choices=[("", "")], default="")
    occupation = SelectField(lazy_gettext("Your position"), choices=occupations, validators=[DataRequired()])
    company_type = SelectField(lazy_gettext("Company Type"), validators=[], choices=[("", "")], default="")
    company_size = SelectField(
        lazy_gettext("Size of your company"),
        choices=company_sizes,
        validators=[DataRequired()],
    )
    company_url = StringField(lazy_gettext("Company URL"), validators=[])
    referred_by = TextAreaField(lazy_gettext("How did you hear about us? (Referral, social media, web search)"))

    consent = BooleanField(lazy_gettext("I agree to"), validators=[])
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = StringField(lazy_gettext("Email"), validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])
    remember_me = BooleanField(lazy_gettext("Remember Me"), validators=[])
    firebase_status = StringField("firebase_status", validators=[])  # for firebase status code


class TokenForm(FlaskForm):
    email = StringField(lazy_gettext("Email"), validators=[DataRequired(), Length(1, 64), Email()])
    firebase_status = StringField("firebase_status", validators=[])  # for firebase status code


class ResetPasswordForm(FlaskForm):
    match_password2 = [
        DataRequired(),
        Length(min=8),
        EqualTo("new_password2", message=lazy_gettext("Passwords must match.")),
    ]
    old_password = PasswordField(
        lazy_gettext("Current password"),
        validators=[],
    )
    new_password = PasswordField(lazy_gettext("New password"), validators=match_password2)
    new_password2 = PasswordField(lazy_gettext("Confirm new password"), validators=[DataRequired()])

    email = StringField(lazy_gettext("Email"), validators=[])  # for autocomplete
    firebase_status = StringField("firebase_status", validators=[])  # for firebase status code
