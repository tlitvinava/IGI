from django.urls import path
from . import views
from autoservice.views import api_map_view
from .views import HomeView
from .views import AboutView
from .views import (HomeView, AboutView, NewsListView, GlossaryView, ContactsView,
                    PrivacyPolicyView, VacanciesView, ReviewsView, PromoCodesView, ServiceListView, ReviewCreateView, SparePartListView, SparePartDetailView)
from .views import ArticleDetailView
from .views import spare_part_delete
from .views import (
    PartnerListView,
    CartView,
    add_to_cart,
    remove_from_cart,
    update_cart_quantity,
    checkout,
    payment_success
)


urlpatterns = [
    # URL главной страницы модуля – список услуг
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    # URL детального просмотра услуги
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    # URL для создания новой услуги
    path('services/create/', views.ServiceCreateView.as_view(), name='service-create'),
    # URL для редактирования услуги
    path('services/<int:pk>/update/', views.ServiceUpdateView.as_view(), name='service-update'),
    # URL для удаления услуги
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service-delete'),
     # URL для регистрации
    path('accounts/register/', views.register, name='register'),
    path('orders/my/', views.MyOrdersListView.as_view(), name='my-orders'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('news/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('home/', HomeView.as_view(), name='home'),
    path('', HomeView.as_view(), name='home'),
    
     # Новый маршрут для страницы профиля:
    path('profile/', views.ProfileView.as_view(), name='profile'),
     # Админ-панель (для пользователей с ролью admin)
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin-panel/orders/', views.OrderAdminListView.as_view(), name='admin-orders'),
    path('admin-panel/orders/<int:pk>/edit/', views.OrderAdminUpdateView.as_view(), name='admin-order-edit'),
    # Добавляйте маршруты для клиентов, запчастей, автосервиса и т.д.
    path('admin-panel/misc/', views.admin_misc_dashboard, name='admin-misc'),
    path('admin-panel/auto/<int:pk>/edit/', views.AutoTypeUpdateView.as_view(), name='admin-autotype-edit'),
    path('admin-panel/auto/<int:pk>/delete/', views.AutoTypeDeleteView.as_view(), name='admin-autotype-delete'),
    path('admin-panel/service/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='admin-service-edit'),
    path('admin-panel/service/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='admin-service-delete'),
    path('admin-panel/spare/<int:pk>/edit/', views.SparePartUpdateView.as_view(), name='admin-sparepart-edit'),
    path('admin-panel/spare/<int:pk>/delete/', views.SparePartDeleteView.as_view(), name='admin-sparepart-delete'),
    #path('admin-panel/spare/delete/<int:pk>/', views.spare_part_delete, name='spare_delete'),
    path('master-panel/', views.MasterDashboardView.as_view(), name='master-dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', AboutView.as_view(), name='about'),
    path('news/', NewsListView.as_view(), name='news'),
    path('glossary/', GlossaryView.as_view(), name='glossary'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('vacancies/', VacanciesView.as_view(), name='vacancies'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
    path('reviews/add/', ReviewCreateView.as_view(), name='add_review'),
    path('promo-codes/', PromoCodesView.as_view(), name='promo_codes'),
    path('api-map/', api_map_view, name='api_map'),
    # Партнёры
    path('partners/', PartnerListView.as_view(), name='partners'),
    # Корзина
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<str:item_type>/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/<str:action>/', update_cart_quantity, name='update_cart_quantity'),
    # Оплата
    path('checkout/', checkout, name='checkout'),
    path('payment-success/', payment_success, name='payment_success'),
    # Товары (запчасти)
    path('spare-parts/<int:pk>/', SparePartDetailView.as_view(), name='sparepart-detail'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('spare-parts/', SparePartListView.as_view(), name='sparepart-list'),



]

        
