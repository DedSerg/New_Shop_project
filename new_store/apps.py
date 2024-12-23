from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'new_store'
#
#     def ready(self):
#        import New_Shop.new_store.signals