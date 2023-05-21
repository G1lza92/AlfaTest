from django.urls import path

from .views import ShoppingAmountAPIView

urlpatterns = [
    path('get-shopping-amount/<str:login>/', ShoppingAmountAPIView.as_view()),
]
