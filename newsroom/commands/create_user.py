import click
from bson import ObjectId
from quart.cli import with_appcontext

from newsroom.types import UserResourceModel
from newsroom.async_utils import run_async_to_sync
from newsroom.users.service import UsersService

from .cli import newsroom_cli


@newsroom_cli.command("create_user")
@click.argument("email")
@click.argument("password")
@click.argument("first_name")
@click.argument("last_name")
@click.argument("is_admin", type=bool)
@with_appcontext
async def create_user(email, password, first_name, last_name, is_admin):
    """Create a user with given email, password, first_name, last_name and is_admin flag.

    If user with given username exists it's noop.

    Example:
    ::

        $ flask newsroom create_user admin@admin.com adminadmin admin admin True
    """
    new_user = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "user_type": "administrator" if is_admin else "public",
        "is_enabled": True,
        "is_approved": True,
        "id": ObjectId(),
    }
    new_user = UserResourceModel.from_dict(new_user)
    user = await UsersService().get_by_email(email)

    if user:
        print("User already exists %s" % str(new_user))
    else:
        print("Creating user...")
        run_async_to_sync(UsersService().create([new_user]))
        print("User created successfully %s" % (new_user.to_dict()))

    return new_user
