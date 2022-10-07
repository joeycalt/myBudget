from django.views import View 
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Budget

class Home(TemplateView):
    template_name = "home.html"

class About(TemplateView):
    template_name = "about.html"

class Signup(View):
    def get(self, request):
        form = UserCreationForm()
        context = {"form": form}
        return render(request, "registration/signup.html", context)
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("budget_form")
        else:
            context = {"form": form}
            return render(request, "registration/signup.html", context)

class BudgetForm(TemplateView):
    model = Budget
    fields = ['budget', 'month']
    template_name = "budget_form.html"
    success_url = "/purchases/"
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BudgetForm, self).form_valid(form)

    def get_success_url(self):
        print(self.kwargs)
        return reverse('purchases', kwargs={'pk': self.object.pk})