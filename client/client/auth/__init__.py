import json
import os

from .login import LoginForm

CREDENTIALS = 'credentials.json'


def create_credentials(client):
    """
    Remember the user's credentials.
    Not in use duo to testing.
    """
    if not os.path.exists(CREDENTIALS):
        form = LoginForm(client)
        form.show()
        form.exec_()

        if form.result:
            with open(CREDENTIALS, 'w') as file:
                json.dump(form.data, file)
            return
    try:
        with open(CREDENTIALS) as file:
            user = json.load(file)
    except json.JSONDecodeError:
        os.remove(CREDENTIALS)
        return create_credentials(client)
    else:
        client.login(**user)
