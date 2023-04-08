import os
import django


def init_django(root_app_name) -> None:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{root_app_name}.settings')
  os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
  django.setup()
