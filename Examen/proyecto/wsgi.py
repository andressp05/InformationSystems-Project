from django.core.wsgi import get_wsgi_application
from dj_static import Cling
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto.settings")
application = get_wsgi_application()
application = Cling(get_wsgi_application())