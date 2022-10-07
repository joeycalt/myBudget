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
from .models import Budget, Purchased, Item

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

class BudgetForm(CreateView):
    model = Purchased
    fields = ['item', 'price', 'date']
    template_name = "budget_form.html"
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BudgetForm, self).form_valid(form)
    def get_success_url(self):
        print(self.kwargs)
        return reverse('budget_detail', kwargs={'pk': self.object.pk})

class BudgetList(TemplateView):
    template_name = "budget_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.request.GET.get("location")
        if location != None:
            context["stores"] = Purchased.objects.filter(name__icontains=location)
            context['header'] = f"Searching through Budget list for {location}"
        else:
            context["stores"] = Purchased.objects.filter(user=self.request.user)
            context['header'] = 'Budget List'
        return context

class BudgetDetail(DetailView):
    model = Purchased
    template_name = "budget_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Item.objects.all()
        return context