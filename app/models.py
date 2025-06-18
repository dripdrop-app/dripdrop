import importlib

from app.base.models import Base  # noqa

APPS = [
    "dripdrop.authentication",
    "dripdrop.music",
    "dripdrop.youtube",
]

for app in APPS:
    importlib.import_module(app + ".models")
