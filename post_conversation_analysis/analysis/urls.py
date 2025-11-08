from django.urls import path
from .views import *

urlpatterns = [
    path("conversations/", ConversationView.as_view()),
    path("analyse/", AnalyseView.as_view()),
    path("reports/", ReportsView.as_view()),
]
