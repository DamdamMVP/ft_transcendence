from django.apps import AppConfig


class DjangoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangoapp'

    def ready(self):
        import djangoapp.consumers  # Late imports to avoid errors