from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.repositories import UserRepository


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Expected Bearer token")

    # Development auth contract: the token is an email address.
    # Production can replace this with Clerk/Supabase/Auth0 JWT verification.
    if "@" not in token:
        raise HTTPException(status_code=401, detail="Invalid development auth token")

    return UserRepository(db).get_or_create(email=token)
