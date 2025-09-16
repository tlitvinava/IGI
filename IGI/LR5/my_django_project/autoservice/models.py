import datetime
from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

def validate_age(value):
    """Валидатор для проверки, что возраст клиента не менее 18 лет."""
    today = datetime.date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Возраст должен быть не менее 18 лет.')

# ---------------------------
# Пользователи
# ---------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('master', 'Мастер'),
        ('client', 'Клиент'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Роль пользователя'
    )
    date_of_birth = models.DateField(verbose_name="Дата рождения", validators=[validate_age])
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$",
            message="Номер телефона должен быть в формате +375 (XX) XXX-XX-XX."
        )],
        verbose_name="Номер телефона",
        blank=True,  # Allow blank
        null=True    # Allow null
    )
    
    def __str__(self):
        return self.username
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_set",
        related_query_name="customuser"
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions_set",
        related_query_name="customuser"
    )

# ---------------------------
# Услуги
# ---------------------------
class Service(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость услуги", validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name} ({self.description})"
    
class PromoCode(models.Model):
    code = models.CharField("Промокод", max_length=50, unique=True)
    discount = models.PositiveIntegerField("Скидка в процентах")
    active = models.BooleanField("Активен", default=True)

    def __str__(self):
        return self.code

class Coupon(models.Model):
    code = models.CharField("Купон", max_length=50, unique=True)
    value = models.DecimalField("Сумма скидки", max_digits=8, decimal_places=2)
    active = models.BooleanField("Активен", default=True)

    def __str__(self):
        return self.code

# ---------------------------
# Клиенты
# ---------------------------
class Client(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    email = models.EmailField(verbose_name="Электронная почта")
    phone = models.CharField(max_length=20, validators=[RegexValidator(
        regex=r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$",
        message="Номер телефона должен быть в формате +375 (XX) XXX-XX-XX."
    )], verbose_name="Телефон")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Пользователь", 
        related_name="client"
    )

    def __str__(self):
        return self.user.__str__()

# ---------------------------
# Специализации мастеров
# ---------------------------
class MasterSpecialization(models.Model):
    name = models.CharField(max_length=100, verbose_name="Специализация")

    def __str__(self):
        return self.name

# ---------------------------
# Мастера
# ---------------------------
class Master(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО мастера")
    email = models.EmailField(verbose_name="Электронная почта мастера")
    phone = models.CharField(max_length=20, validators=[RegexValidator(
        regex=r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$",
        message="Номер телефона должен быть в формате +375 (XX) XXX-XX-XX."
    )], verbose_name="Телефон")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Пользователь", 
        related_name="master"
    )
    specializations = models.ManyToManyField(
        MasterSpecialization, 
        blank=True, 
        verbose_name="Специализации", 
        related_name="masters"
    )
    schedule = models.TextField(blank=True, verbose_name="Расписание работы")

    def __str__(self):
        return self.user.__str__()

# ---------------------------
# Типы авто
# ---------------------------
class AutoType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип автомобиля")
    description = models.TextField(blank=True, verbose_name="Описание типа авто")

    def __str__(self):
        return self.name

# ---------------------------
# Запчасти
# ---------------------------
class SparePart(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название запчасти")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена запчасти",
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True, verbose_name="Описание запчасти")
    image = models.ImageField(
        upload_to='spareparts/',
        null=True,
        blank=True,
        verbose_name="Изображение запчасти"
    )

    def __str__(self):
        return self.name

# ---------------------------
# Заказы (Ремонты)
# ---------------------------
class Order(models.Model):
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        verbose_name="Клиент", 
        related_name="orders"
    )
    master = models.ForeignKey(
        Master, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Мастер", 
        related_name="orders"
    )
    auto_type = models.ForeignKey(
        AutoType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Тип авто"
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Услуга"
    )
    spare_parts = models.ManyToManyField(
        SparePart, 
        blank=True, 
        verbose_name="Использованные запчасти", 
        related_name="orders"
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    notes = models.TextField(blank=True, verbose_name="Дополнительные примечания")

    def __str__(self):
        return f"Заказ №{self.id} от {self.order_date.strftime('%d/%m/%Y')}"

    @property
    def total_cost(self):
        service_cost = self.service.price if self.service else 0
        parts_cost = sum(part.price for part in self.spare_parts.all())
        return service_cost + parts_cost

# ---------------------------
# Новостные статьи / Новости (Article)
# ---------------------------
class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок статьи")
    summary = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(
        verbose_name="Полный текст статьи",
        default="""В статье подробно рассмотрены инновационные технологии, использованные при разработке нового электромобиля, его характеристики, особенности эксплуатации и преимущества перед традиционными моделями.

Новая модель обладает увеличенным запасом хода благодаря усовершенствованной батарее, а современные системы безопасности обеспечивают высокий уровень защиты водителя и пассажиров.

Эксперты отмечают, что этот запуск может стать прорывом в индустрии, а автопроизводитель планирует масштабировать производство для удовлетворения растущего спроса на экологичные автомобили."""
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    image = models.ImageField(
        upload_to='articles/', 
        null=True, 
        blank=True, 
        verbose_name="Изображение"
    )

    def __str__(self):
        return self.title

# ---------------------------
# Информация о компании (CompanyInfo)
# ---------------------------
class CompanyInfo(models.Model):
    logo = models.ImageField(
        upload_to='company/', 
        null=True, 
        blank=True, 
        verbose_name="Логотип"
    )
    description = models.TextField(verbose_name="Описание компании")
    history = models.TextField(verbose_name="История по годам")
    details = models.TextField(verbose_name="Реквизиты")

    def __str__(self):
        return "Информация о компании"

# ---------------------------
# Словарь терминов и понятий (GlossaryTerm)
# ---------------------------
class GlossaryTerm(models.Model):
    term = models.CharField(max_length=100, verbose_name="Термин")
    definition = models.TextField(verbose_name="Определение")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.term

# ---------------------------
# Контакты (Contact)
# ---------------------------
class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    photo = models.ImageField(
        upload_to='contacts/',
        null=True,
        blank=True,
        verbose_name="Фото"
    )

    def __str__(self):
        return self.name

# ---------------------------
# Вакансии (Vacancy)
# ---------------------------
class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание вакансии")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

# ---------------------------
# Отзывы (Review)
# ---------------------------
class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя автора отзыва")
    rating = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Оценка")
    text = models.TextField(verbose_name="Текст отзыва")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.name
    
# ---------------------------
# Партнёры (Partner)
# ---------------------------
class Partner(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название компании")
    logo = models.ImageField(upload_to="partners/", verbose_name="Логотип", null=True, blank=True)
    website = models.URLField(verbose_name="Сайт компании")

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------------
# Элементы корзины (CartItem)
# ---------------------------
class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Пользователь"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
        verbose_name="Услуга"
    )
    spare_part = models.ForeignKey(
        SparePart,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
        verbose_name="Запчасть"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество", validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        ordering = ["-added_at"]
        constraints = [
            # Ровно один тип позиции: либо услуга, либо запчасть
            models.CheckConstraint(
                check=(
                    # (service IS NOT NULL AND spare_part IS NULL) OR (service IS NULL AND spare_part IS NOT NULL)
                    (Q(service__isnull=False) & Q(spare_part__isnull=True)) |
                    (Q(service__isnull=True) & Q(spare_part__isnull=False))
                ),
                name="cartitem_exactly_one_of_service_or_sparepart"
            )
        ]

    def __str__(self):
        title = self.service.name if self.service else self.spare_part.name
        return f"{title} × {self.quantity}"

    @property
    def unit_price(self):
        if self.service:
            return self.service.price
        if self.spare_part:
            return self.spare_part.price
        return 0

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

# ---------------------------
# Платёж (Payment)
# ---------------------------
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидание"
        PAID = "paid", "Оплачен"
        FAILED = "failed", "Ошибка"
        CANCELED = "canceled", "Отменён"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Заказ"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус")
    method = models.CharField(max_length=50, verbose_name="Способ оплаты", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    transaction_id = models.CharField(max_length=100, verbose_name="ID транзакции", blank=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Платёж за заказ #{self.order_id} — {self.get_status_display()}"
