from datetime import datetime, timedelta, timezone
from functools import wraps
import os

import jwt
from flask import current_app, request, jsonify, g

from app import db
from app.models import User


def _get_jwt_secret() -> str:
  """
  Resolve the JWT secret key from config or environment.
  Falls back to Flask SECRET_KEY for convenience in dev.
  """
  cfg = current_app.config
  return (
      cfg.get("JWT_SECRET_KEY")
      or os.getenv("JWT_SECRET_KEY")
      or cfg.get("SECRET_KEY")
      or "dev-secret-change-me"
  )

