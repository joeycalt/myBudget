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
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from time import timezone
import logging

logger = logging.getLogger(__name__)

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
            return render(request, "registration/signup.html", 'crispy_forms.html', {"form": form})
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('username', css_class='form-group col-4'),
                Div('password', css_class='form-group col-4'),
                Div('passsword1', css_class='form-group'),
                Div('passsword2', css_class='form-group'),
                css_class='form-row'
            ),
        ),

class BudgetList(TemplateView):
    template_name = "budget_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get("month")
        current_month = datetime.now().strftime('%B')
        if month != None:
            context["stores"] = Budget.objects.filter(month__icontains=month, user=self.request.user).order_by('-id')
            context['header'] = f"Searching through Budget list for the month of {month}"
        else:
            context["stores"] = Budget.objects.filter(user=self.request.user).order_by('-id')
            context['header'] = 'Budget List'
        try:
            current_budget = Budget.objects.get(
                month__iexact=current_month,  # Case-insensitive match
                user=self.request.user
            )
            context["current_budget"] = current_budget
        except Budget.DoesNotExist:
            context["current_budget"] = None
        return context

class BudgetDetail(View):
    def get(self, request, pk):
        budget = Budget.objects.get(pk=pk, user=request.user)
        return render(request, 'budget_detail.html', {'budget': budget})

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('amount', css_class='form-inputs'),
                Div('month', css_class='form-inputs'),
                css_class='form-row'
            ),
        ),

# class BudgetForm(View):
#     def get(self, request):
#         return render(request, 'budget_form.html')

#     def post(self, request):
#         try:
#             month = request.POST.get("month")  # "August"
#             amount = request.POST.get("amount")  # "5000" (string from form)
#             logger.info("Received: month=%s, amount=%s (type=%s)", month, amount, type(amount))
#             # Explicitly convert amount to Decimal
#             budget = Budget.objects.create(
#                 user=request.user,
#                 month=month,
#                 amount=Decimal(amount)  # Ensure Decimal conversion
#             )
#             logger.info("Budget created: id=%s, amount=%s (type=%s)", budget.pk, budget.amount, type(budget.amount))
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 date_range = budget.get_date_range()
#                 logger.info("Date range: %s", date_range)
#                 spent = budget.get_spent_amount()
#                 logger.info("Spent amount: %s (type=%s)", spent, type(spent))
#                 remaining = budget.get_remaining_amount()
#                 logger.info("Remaining: %s (type=%s)", remaining, type(remaining))
#                 response_data = {
#                     'success': True,
#                     'budget': {
#                         'id': budget.pk,
#                         'month': budget.month,
#                         'date_range': date_range,
#                         'amount': str(budget.amount),
#                         'remaining': str(remaining)
#                     }
#                 }
#                 logger.info("Response data: %s", response_data)
#                 return JsonResponse(response_data)
#             return redirect('budget_list')
#         except Exception as e:
#             logger.error("Error in BudgetForm.post: %s", str(e), exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)

class BudgetCreate(LoginRequiredMixin, View):
    def get(self, request, pk):
        budget = Budget.objects.get(pk=pk, user=request.user)
        return render(request, 'add_expense.html', {'budget': budget})

    def post(self, request, pk):
        budget = Budget.objects.get(pk=pk, user=request.user)
        name = request.POST.get("name")
        title = request.POST.get("title")
        price = request.POST.get("price").replace('$', '').strip()
        date = request.POST.get("date")
        
        try:
            new_item = Item.objects.create(
                name=name,
                title=title,
                price=Decimal(price),
                date=date
            )
            new_item.buys.add(budget)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX response
                return JsonResponse({
                    'success': True,
                    'remaining': str(budget.get_remaining_amount()),
                     'item': {
                    'name': new_item.name,
                    'title': new_item.title,
                    'price': str(new_item.price),
                    'date': str(new_item.date),
                    'id': new_item.pk  # For edit/delete links
                }
                })
            return redirect('budget_list')
        except ValueError as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            return redirect('budget_list')

class ItemUpdate(View):
    def post(self, request, budget_pk, pk):
        budget = get_object_or_404(Budget, pk=budget_pk, user=request.user)
        item = get_object_or_404(Item, pk=pk, buys=budget)
        
        item.name = request.POST.get("name")
        item.title = request.POST.get("title")
        item.price = request.POST.get("price").replace('$', '').strip()
        item.date = request.POST.get("date")
        item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item': {
                    'name': item.name,
                    'title': item.title,
                    'price': str(item.price),
                    'date': str(item.date),
                },
                'remaining': str(budget.get_remaining_amount())
            })
        return redirect('budget_detail', pk=budget_pk)

class ItemDelete(DeleteView):
    model = Item
    template_name = "item_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.object
        context['budget'] = Budget.objects.get(pk=self.kwargs['budget_pk'])
        return context

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
            budget_pk = self.kwargs['budget_pk']
            if obj.buys.filter(pk=budget_pk, user=self.request.user).exists():
                return obj
            logger.error("Permission denied: Item %s not in Budget %s for User %s", obj.pk, budget_pk, self.request.user)
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return None
            raise PermissionDenied
        except Item.DoesNotExist:
            logger.error("Item not found: id=%s, budget_pk=%s", self.kwargs.get('pk'), self.kwargs['budget_pk'])
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return None
            raise Http404

    def form_valid(self, form):
        self.object = self.get_object()
        budget_pk = self.kwargs['budget_pk']

        if self.object is None:
            return JsonResponse({'success': False, 'error': 'Item not found or access denied'}, status=404)

        try:
            self.object.delete()
            logger.info("Item deleted: id=%s, budget_pk=%s", self.object.pk, budget_pk)

            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True}, status=200)

            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            logger.error("Error in ItemDelete.form_valid: %s", str(e))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            raise

    def get_success_url(self):
        return reverse('budget_detail', kwargs={'pk': self.kwargs['budget_pk']})

class BudgetDelete(DeleteView):
    model = Budget
    template_name = "budget_delete.html"
    success_url = "/budget/"

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
            if obj.user == self.request.user:
                return obj
            logger.error("Permission denied: Budget %s, User %s", obj.pk, self.request.user)
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return None
            raise PermissionDenied
        except Budget.DoesNotExist:
            logger.error("Budget not found: id=%s", self.kwargs.get('pk'))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return None
            raise Http404

    def form_valid(self, form):
        self.object = self.get_object()
        if self.object is None:
            return JsonResponse({'success': False, 'error': 'Budget not found or access denied'}, status=404)

        try:
            self.object.delete()
            logger.info("Budget deleted: id=%s", self.object.pk)

            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True}, status=200)

            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            logger.error("Error in BudgetDelete.form_valid: %s", str(e))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            raise

    def get_success_url(self):
        return reverse('budget_list')