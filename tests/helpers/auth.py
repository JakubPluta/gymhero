from gymhero.models.user import User
from gymhero.security import create_access_token


def auth_headers(user: User | int) -> dict[str, str]:
    # Accepts a User or a bare id, so a token can be minted for an id that has
    # no matching row (to hit the "user not found" path).
    subject = user.id if isinstance(user, User) else user
    return {"Authorization": f"Bearer {create_access_token(subject)}"}
