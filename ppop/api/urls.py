from django.urls import path
from api import views


urlpatterns = [
    path('doc/', views.api_doc),
    path('start/', views.Start.as_view()),
    path('stop/', views.Stop.as_view()),
    path('params/', views.Params.as_view()),
    path('track/', views.Track.as_view()),
    path('status/', views.Status.as_view()),

]

