from django.views import View 
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
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

class BudgetList(TemplateView):
    template_name = "budget_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time = self.request.GET.get("budget")
        if time != None:
            context["stores"] = Budget.objects.filter(name__icontains=time)
            context['header'] = f"Searching through Budget list for {time}"
        else:
            context["stores"] = Budget.objects.all()
            context['header'] = 'Budget List'
        return context

class BudgetDetail(DetailView):
    model = Budget
    template_name = "budget_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Item.objects.filter()
        return context
        

class BudgetListAssoc(View):
    def get(self, request, pk, buy_pk):
        assoc = request.GET.get("assoc")
        if assoc == "remove":
            Item.objects.get(pk=pk).buys.remove(buy_pk)
        if assoc == "add":
            Item.objects.get(pk=pk).buys.add(buy_pk)
        return redirect('/purchases/')

class BudgetForm(CreateView):
    model = Budget
    fields = ['amount', 'month']
    template_name = 'budget_form.html'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BudgetForm, self).form_valid(form)
    def get_success_url(self):
        print(self.kwargs)
        return reverse('budget_list') 

class BudgetCreate(View):
    def post(self, request, pk):
        name = request.POST.get("name")
        title = request.POST.get("title")
        price = request.POST.get("price")
        date = request.POST.get("date")
        bought = Budget.objects.get(pk=pk)
        new_item = Item.objects.create(name=name, title=title, price=price, date=date)
        new_item.buys.add(bought.pk)
        return redirect('budget_detail', pk=pk)

class ItemUpdate(UpdateView):
    model = Item
    fields = ['name', 'title', 'price', 'date']
    template_name = "item_update.html"
    def get_success_url(self):
        return reverse('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})
    

class BudgetDelete(DeleteView):
    model = Budget
    template_name = "budget_delete.html"
    success_url = "/budget/"