from config.settings import *  # noqa: F401,F403

# testing db
DATABASES["default"]["NAME"] = "test_fmg"  # type: ignore[index]