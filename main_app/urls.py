from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('about/', views.About.as_view(), name="about"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.Signup.as_view(), name="signup"),
    path('budget/', views.BudgetList.as_view(), name="budget_list"),
    path('budget/new/', views.BudgetForm.as_view(), name="budget_form"),
    path('budget/<int:pk>/', views.BudgetDetail.as_view(), name="budget_detail"),
]