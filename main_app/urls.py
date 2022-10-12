from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('about/', views.About.as_view(), name="about"),
    # path('purchases/', views.AddPurchase.as_view(), name="purchases_done"),
    path('accounts/signup/', views.Signup.as_view(), name="signup"),
    path('budget/', views.BudgetList.as_view(), name="budget_list"),
    path('budget/new/', views.BudgetForm.as_view(), name="budget_form"),
    path('budget/<int:pk>/', views.BudgetDetail.as_view(), name='budget_detail'),
    path('budget/<int:pk>/buys/new/', views.BudgetCreate.as_view(), name="budget_create"),
    # path('budget/<int:pk>/buys/<int:buy_pk>/', views.BudgetListAssoc.as_view(), name="budget_list_assoc"),
    path('budget/<int:budget_pk>/item/<int:pk>/update/', views.ItemUpdate.as_view(), name="item_update"),
    path('budget/<int:pk>/delete',views.BudgetDelete.as_view(), name="budget_delete"),
]