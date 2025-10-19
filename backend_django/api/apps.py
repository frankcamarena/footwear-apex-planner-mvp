# backend_django/api/apps.py

from django.apps import AppConfig
# IMPORTACIONES NECESARIAS PARA EL WORKAROUND
from django.dispatch import receiver
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.signals import connection_created


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Aplica un fix para el error 'Cannot use MongoClient after close'
        que ocurre con Djongo/PyMongo al intentar reutilizar conexiones.
        """
        # 1. Función que cancela el chequeo de cierre automático para djongo.
        @receiver(connection_created)
        def skip_close_if_unusable(connection, **kwargs):
            if connection.vendor == 'djongo':
                # Sobreescribe la función de cierre para evitar el error.
                connection.close_if_unusable_or_obsolete = lambda: None
        
        # 2. Reemplazar la función de cierre en la clase base para asegurar que no se ejecute.
        # Esto es un refuerzo para el fix, especialmente en entornos de desarrollo.
        BaseDatabaseWrapper.close_if_unusable_or_obsolete = lambda self: None