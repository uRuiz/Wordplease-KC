from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from blogs import urls as blogs_urls, api_urls as blogs_api_urls
from django.conf.urls.static import static
from users import urls as users_urls, api_urls as users_api_urls
from files import api_urls as files_api_urls

urlpatterns = [
    # Django admin URLs
    url(r'^admin/', include(admin.site.urls)),

    # Blogs URLs
    url(r'^', include(blogs_urls)),

    # Users URLs
    url(r'^', include(users_urls)),

    # API URLs
    url(r'^api/', include(blogs_api_urls)),
    url(r'^api/', include(users_api_urls)),
    url(r'^api/', include(files_api_urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # support for media files
