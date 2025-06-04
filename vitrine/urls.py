from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('cv/', views.cv, name='cv'),
    path('coiffeuse/', views.coiffeuse, name='coiffeuse'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedbacks/', views.liste_feedbacks, name='liste_feedbacks'),
    path('feedback/repondre/<int:feedback_id>/', views.repondre_feedback, name='repondre_feedback'),
    path('commande/', views.commande, name='commande'),
    path('sms-webhook/', views.sms_webhook, name='sms_webhook'),
    path('politique-de-confidentialite/', views.politique_confidentialite, name='politique'),
    path('mentions-legales/', views.mentions_legales, name='mentions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)