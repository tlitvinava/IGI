from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Service
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from .models import Service
from .models import Order, Client, Master
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from .forms import AutoTypeForm, ServiceForm, SparePartForm
from django.contrib.auth import logout
from .models import Article, CompanyInfo, GlossaryTerm, Contact, Vacancy, Review, PromoCode


from django.views.generic import ListView
from .models import Service

class ServiceListView(ListView):
    model = Service
    template_name = "autoservice/services.html"
    context_object_name = "services"
    paginate_by = 10  # если требуется разбивка по страницам, можно убрать этот параметр

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

# autoservice/views.py
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import Review
from .forms import ReviewForm

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/add_review.html"  # Можно хранить шаблон в папке reviews или pages
    success_url = reverse_lazy('reviews')  # После отправки возвращаемся к списку отзывов

    def form_valid(self, form):
        # Автоматически подставляем имя автора отзыва как username текущего пользователя
        form.instance.name = self.request.user.username
        return super().form_valid(form)

from django.views.generic import DetailView
from .models import Article

class ArticleDetailView(DetailView):
    model = Article
    template_name = "pages/article_detail.html"
    context_object_name = "article"

from django.views.generic import TemplateView
from .models import Contact, Master, CustomUser

class ContactsView(TemplateView):
    template_name = "pages/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        context['masters'] = Master.objects.all()
        context['admins'] = CustomUser.objects.filter(role='admin')
        return context


# Детальный просмотр услуги (Read – detail)
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
    

# class MasterDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
#     template_name = 'autoservice/master_dashboard.html'
    
#     def test_func(self):
#         # Проверяем, что пользователь состоит в группе "Masters"
#         return self.request.user.groups.filter(name='Masters').exists()

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

# autoservice/views.py (дополнение)
class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ['master', 'auto_type', 'service', 'spare_parts', 'notes']  
    # Здесь можно добавить любые поля, которые вы хотите предложить пользователю.
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("my-orders")  

    def form_valid(self, form):
        # Назначаем клиента из связанного объекта пользователя.
        form.instance.client = self.request.user.client  
        return super().form_valid(form)


class HomeView(TemplateView):
    template_name = "autoservice/home.html"

def handle404(request, exception):
    # Вместо показа стандартной 404-страницы делаем редирект на главную /home
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
    
# autoservice/views.py
from django.views.generic import ListView
from .models import Order  # ваша модель Order (связана с Client, Master, и т.д.)

class OrderAdminListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "autoservice/admin/orders_list.html"
    context_object_name = "orders"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

from django.views.generic import UpdateView
from django.urls import reverse_lazy

class OrderAdminUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    fields = ['client', 'master', 'auto_type', 'service', 'spare_parts', 'notes']
    template_name = "autoservice/admin/order_form.html"
    success_url = reverse_lazy("admin-orders")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)


# autoservice/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import AutoType, Service, SparePart
from .forms import AutoTypeForm, ServiceForm, SparePartForm

@login_required
def admin_misc_dashboard(request):
    # Доступ разрешён только администратору
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

# autoservice/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from .models import AutoType, Service, SparePart

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

# Представление для удаления запчасти
class SparePartDeleteView(LoginRequiredMixin, DeleteView):
    model = SparePart
    template_name = "autoservice/admin/spare_confirm_delete.html"
    success_url = reverse_lazy("admin-misc")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "admin":
            raise PermissionDenied("У вас нет доступа к админ-панели.")
        return super().dispatch(request, *args, **kwargs)

# autoservice/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.db.models import Sum
from .models import Order

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

from django.views.generic import TemplateView
from .models import Service, PromoCode, Coupon

class HomeView(TemplateView):
    template_name = "autoservice/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все услуги без применения фильтров
        context['services'] = Service.objects.all()
        # Получаем активные промокоды и купоны для отображения
        context['promo_codes'] = PromoCode.objects.filter(active=True)
        context['coupons'] = Coupon.objects.filter(active=True)
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

from django.shortcuts import render

def api_map_view(request):
    return render(request, "autoservice/api_map.html")
