from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout

from django.views.generic import ListView, TemplateView, RedirectView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse

from .models import Partner, CartItem, Service, SparePart, Payment, Order
from django.db.models import Sum

from .models import (
    Service,
    Order,
    Client,
    Master,
    Article,
    CompanyInfo,
    GlossaryTerm,
    Contact,
    Vacancy,
    Review,
    PromoCode,
    CustomUser,
    AutoType,
    SparePart,
    Coupon
)
from .forms import CustomUserCreationForm, AutoTypeForm, ServiceForm, SparePartForm, ReviewForm

class ServiceListView(ListView):
    model = Service
    template_name = "autoservice/services.html"
    context_object_name = "services"
    paginate_by = 10  

    def get_queryset(self):
        queryset = Service.objects.all()
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        category_id = self.request.GET.get('category')
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        if category_id:
            queryset = queryset.filter(category__id=category_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = {
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
        }
        return context

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/add_review.html"  # Можно хранить шаблон в папке reviews или pages
    success_url = reverse_lazy('reviews')  # После отправки возвращаемся к списку отзывов

    def form_valid(self, form):
        # Автоматически подставляем имя автора отзыва как username текущего пользователя
        form.instance.name = self.request.user.username
        return super().form_valid(form)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "pages/article_detail.html"
    context_object_name = "article"


class ContactsView(TemplateView):
    template_name = "pages/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['masters'] = Master.objects.all()
        context['admins'] = CustomUser.objects.filter(role='admin')
        return context


class ServiceDetailView(DetailView):
    model = Service
    context_object_name = 'service'
    template_name = 'autoservice/service_detail.html'

# Создание услуги (Create)
class ServiceCreateView(CreateView):
    model = Service
    fields = ['name', 'description', 'price', 'service_type']
    template_name = 'autoservice/service_form.html'

    def get_success_url(self):
        # После создания перенаправляем на детальный просмотр созданной услуги
        return reverse('service-detail', kwargs={'pk': self.object.pk})

# Обновление услуги (Update)
class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['name', 'description', 'price', 'service_type']
    template_name = 'autoservice/service_form.html'

    def get_success_url(self):
        return reverse('service-detail', kwargs={'pk': self.object.pk})

# Удаление услуги (Delete)
class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'autoservice/service_confirm_delete.html'
    success_url = reverse_lazy('service-list')

def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно. Теперь вы можете войти.')
            return redirect('login')  # имя URL для входа из встроенных URL-ов
    else:
        form = UserCreationForm()
    return render(request, 'autoservice/register.html', {'form': form})

@login_required
def secret_page(request):
    return HttpResponse("Эта страница доступна только авторизованным пользователям.")

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    fields = ['name', 'description', 'price', 'service_type']
    template_name = 'autoservice/service_form.html'

    def get_success_url(self):
        return reverse('service-detail', kwargs={'pk': self.object.pk})
    

def custom_404(request, exception):
    """
    Кастомный обработчик ошибки 404, который рендерит главную страницу.
    """
    services = Service.objects.all()  # если хотите вывести перечень услуг
    return render(request, 'autoservice/home.html', {'services': services}, status=404)

class MyOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/my_orders.html"  # Шаблон для списка заказов
    context_object_name = "orders"

    def get_queryset(self):
        # Предполагается, что для клиента имеется связь: request.user.client
        client_obj = self.request.user.client  
        return Order.objects.filter(client=client_obj).order_by("-order_date")

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ['master', 'auto_type', 'service', 'spare_parts', 'notes']  
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("my-orders")  

    def form_valid(self, form):
        form.instance.client = self.request.user.client  
        return super().form_valid(form)


class HomeView(TemplateView):
    template_name = "autoservice/home.html"

def handle404(request, exception):
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Поле birth_day уже есть в форме и будет сохранено для пользователя
            user.date_of_birth = form.cleaned_data.get('birth_day')
            user.save()
            role = form.cleaned_data.get('role')
            if role == 'client':
                Client.objects.create(user=user)
            elif role == 'master':
                Master.objects.create(user=user)
            messages.success(request, "Регистрация прошла успешно! Теперь вы можете войти.")
            return redirect('login')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()
    return render(request, "autoservice/register.html", {"form": form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "autoservice/profile.html"


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "autoservice/admin_dashboard.html"
    
    def dispatch(self, request, *args, **kwargs):
        # Доступ разрешён только администраторам
        if request.user.role != 'admin':
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)
    

class OrderAdminListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "autoservice/admin/orders_list.html"
    context_object_name = "orders"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

class OrderAdminUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    fields = ['client', 'master', 'auto_type', 'service', 'spare_parts', 'notes']
    template_name = "autoservice/admin/order_form.html"
    success_url = reverse_lazy("admin-orders")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def admin_misc_dashboard(request):
    if request.user.role != 'admin':
        raise PermissionDenied("У вас нет доступа к админ-панели.")

    # Используем префиксы, чтобы различать формы, если они отправляются на одной странице.
    auto_form = AutoTypeForm(prefix='auto')
    service_form = ServiceForm(prefix='service')
    spare_form = SparePartForm(prefix='spare')

    if request.method == 'POST':
        # Определяем, какая форма была отправлена, по наличию уникального имени кнопки
        if 'auto-submit' in request.POST:
            auto_form = AutoTypeForm(request.POST, prefix='auto')
            if auto_form.is_valid():
                auto_form.save()
                return redirect('admin-misc')
        elif 'service-submit' in request.POST:
            service_form = ServiceForm(request.POST, prefix='service')
            if service_form.is_valid():
                service_form.save()
                return redirect('admin-misc')
        elif 'spare-submit' in request.POST:
            spare_form = SparePartForm(request.POST, prefix='spare')
            print(spare_form)
            if spare_form.is_valid():
                spare_form.save()
                return redirect('admin-misc')

    auto_types = AutoType.objects.all()
    services = Service.objects.all()
    spare_parts = SparePart.objects.all()
    
    context = {
        'auto_form': auto_form,
        'service_form': service_form,
        'spare_form': spare_form,
        'auto_types': auto_types,
        'services': services,
        'spare_parts': spare_parts,
    }
    return render(request, 'autoservice/admin/misc_dashboard.html', context)

# Представление для редактирования типа авто
class AutoTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AutoType
    fields = ['name']
    template_name = "autoservice/admin/auto_form.html"
    success_url = reverse_lazy("admin-misc")  # Редирект в общий раздел справочников

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

# Представление для удаления типа авто
class AutoTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AutoType
    template_name = "autoservice/admin/auto_confirm_delete.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

# Представление для редактирования услуги
class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    fields = ['name', 'price']
    template_name = "autoservice/admin/service_form.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

# Представление для удаления услуги
class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    template_name = "autoservice/admin/service_confirm_delete.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

# Представление для редактирования запчасти
class SparePartUpdateView(LoginRequiredMixin, UpdateView):
    model = SparePart
    fields = ['name', 'price', 'image']
    template_name = "autoservice/admin/spare_form.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

#Представление для удаления запчасти
class SparePartDeleteView(LoginRequiredMixin, DeleteView):
    model = SparePart
    template_name = "autoservice/admin/spare_confirm_delete.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

def spare_part_delete(request, pk):
    spare = get_object_or_404(SparePart, pk=pk)
    if request.user.role != "admin":
        raise PermissionDenied("У вас нет доступа к админ-панели.")
    if request.method == "POST":
        spare.delete()
        return redirect(reverse_lazy("admin-misc"))
    
    return render(request, "autoservice/admin/spare_confirm_delete.html", {"object": spare})

class MasterDashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "autoservice/master/dashboard.html"  # Шаблон для списка заказов мастера
    context_object_name = "orders"

    def get_queryset(self):
        master_obj = self.request.user.master
        return Order.objects.filter(master=master_obj).order_by("-order_date")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Агрегация итоговой стоимости заказов по каждому клиенту
        aggregated = {}
        for order in self.get_queryset():
            # Предполагается, что у модели Client есть связь user с полем username
            client_username = order.client.user.username
            aggregated[client_username] = aggregated.get(client_username, 0) + order.total_cost
        context['aggregated_totals'] = aggregated
        return context


def logout_view(request):
    logout(request)
    return redirect('home') 

class HomeView(TemplateView):
    template_name = "autoservice/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Последняя статья
        context["latest_article"] = Article.objects.order_by('-pub_date').first()
        # Списки для главной
        context["services"] = Service.objects.all()[:5]
        context["spare_parts"] = SparePart.objects.all()[:5]
        # Промокоды и купоны
        context["promo_codes"] = PromoCode.objects.filter(active=True)
        context["coupons"] = Coupon.objects.filter(active=True)
        return context


class AboutView(TemplateView):
    template_name = "autoservice/about.html"

# Новости: список статей с заголовком, кратким описанием, картинкой и кнопкой "Читать далее"
class NewsListView(ListView):
    model = Article
    template_name = "pages/news.html"
    context_object_name = "articles"
    ordering = ['-pub_date']

# Словарь терминов и понятий: список вопросов и ответов
class GlossaryView(ListView):
    model = GlossaryTerm
    template_name = "pages/glossary.html"
    context_object_name = "terms"
    ordering = ['-date_added']

# Контакты: информация о сотрудниках, телефонах и т.д.
class ContactsView(TemplateView):
    template_name = "pages/contacts.html"

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         # Допустим, у вас есть модель Contact, чтобы хранить контактную информацию
         context['contacts'] = Contact.objects.all()
         return context

# Политика конфиденциальности: пустая страница или с базовым текстом
class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy_policy.html"

# Вакансии: список вакансий
class VacanciesView(ListView):
    model = Vacancy
    template_name = "pages/vacancies.html"
    context_object_name = "vacancies"

# Отзывы: список отзывов; кнопка "Добавить отзыв" ведет к форме
class ReviewsView(ListView):
    model = Review
    template_name = "pages/reviews.html"
    context_object_name = "reviews"
    ordering = ['-date_added']

# Промокоды и купоны: список актуальных и архивных промокодов
class PromoCodesView(ListView):
    model = PromoCode
    template_name = "pages/promo_codes.html"
    context_object_name = "promo_codes"

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def api_map_view(request):
    return render(request, "autoservice/api_map.html")

def statistics_view(request):
    # Проверка доступа: только admin или master
    print ("fcvgjjnl,")
    if request.user.role not in ["admin", "master"]:
        raise PermissionDenied("У вас нет доступа к данной странице.")
    print ("456")
    return render(request, "autoservice/statistics.html")


# --- Партнёры ---
class PartnerListView(ListView):
    model = Partner
    template_name = "pages/partners.html"
    context_object_name = "partners"
    ordering = ["name"]


# --- Корзина ---
@method_decorator(login_required, name='dispatch')
class CartView(TemplateView):
    template_name = "pages/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = CartItem.objects.filter(user=self.request.user)
        total = sum(item.subtotal for item in cart_items)
        context["cart_items"] = cart_items
        context["total"] = total
        return context


@login_required
def add_to_cart(request, item_type, pk):
    """item_type: 'service' или 'spare'"""
    if item_type == "service":
        service = get_object_or_404(Service, pk=pk)
        CartItem.objects.create(user=request.user, service=service, quantity=1)
    elif item_type == "spare":
        spare = get_object_or_404(SparePart, pk=pk)
        CartItem.objects.create(user=request.user, spare_part=spare, quantity=1)
    return redirect("cart")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    return redirect("cart")


@login_required
def update_cart_quantity(request, pk, action):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    if action == "inc":
        item.quantity += 1
    elif action == "dec" and item.quantity > 1:
        item.quantity -= 1
    item.save()
    return redirect("cart")


# --- Оплата ---
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect("cart")

    # Создаём заказ
    order = Order.objects.create(client=request.user.client)
    for item in cart_items:
        if item.service:
            order.service = item.service
        if item.spare_part:
            order.spare_parts.add(item.spare_part)
    order.save()

    # Создаём платёж
    total_amount = sum(item.subtotal for item in cart_items)
    Payment.objects.create(order=order, amount=total_amount, status=Payment.Status.PAID)

    # Очищаем корзину
    cart_items.delete()

    return redirect(reverse("payment_success"))


@login_required
def payment_success(request):
    return render(request, "pages/payment_success.html")

# --- Список запчастей ---
class SparePartListView(ListView):
    model = SparePart
    template_name = "pages/sparepart_list.html"
    context_object_name = "spare_parts"
    ordering = ["name"]

# --- Детальная страница запчасти ---
class SparePartDetailView(DetailView):
    model = SparePart
    template_name = "pages/sparepart_detail.html"
    context_object_name = "spare_part"
