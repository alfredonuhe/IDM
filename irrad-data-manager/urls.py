from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    # Examples:
    # url(r'^$', 'test2_samples_manager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'', include('samples_manager.urls', namespace="samples_manager")),
    #url(r'^samples_manager/',
    #    include('samples_manager.urls', namespace="samples_manager")),
    url(r'^admin/', admin.site.urls),
    #url(r'^terms_conditions/',
    #    TemplateView.as_view(template_name='terms_conditions.html'),
    #    name='terms_conditions'),
    #url(r'^fluence_conversion/',
    #    TemplateView.as_view(template_name='fluence_conversion.html'),
    #    name='fluence_conversion'),
]
