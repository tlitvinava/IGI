from django.test import TestCase
from autoservice.models import (
    Service,
    SparePart,
    PromoCode,
    Coupon,
    Article,
    GlossaryTerm,
    Vacancy,
    Contact,
    CompanyInfo,
    Review
)

class ServiceModelTest(TestCase):
    def test_service_str(self):
        service = Service.objects.create(
            name="ТО",
            description="Регулярное техническое обслуживание",
            price=100.00
        )
        # Метод __str__ возвращает строку в формате "Название (Описание)"
        self.assertEqual(str(service), "ТО (Регулярное техническое обслуживание)")
        self.assertEqual(service.price, 100.00)

class SparePartModelTest(TestCase):
    def test_sparepart_str(self):
        part = SparePart.objects.create(
            name="Фильтр",
            price=20.00,
            description="Воздушный фильтр"
        )
        self.assertEqual(str(part), "Фильтр")
        self.assertEqual(part.price, 20.00)

class PromoCodeModelTest(TestCase):
    def test_promocode_str_and_discount(self):
        promo = PromoCode.objects.create(
            code="PROMO10",
            discount=10,
            active=True
        )
        self.assertEqual(str(promo), "PROMO10")
        self.assertEqual(promo.discount, 10)

class CouponModelTest(TestCase):
    def test_coupon_str_and_value(self):
        coupon = Coupon.objects.create(
            code="COUPON5",
            value=5.00,
            active=True
        )
        self.assertEqual(str(coupon), "COUPON5")
        self.assertEqual(coupon.value, 5.00)

class ArticleModelTest(TestCase):
    def test_article_default_content(self):
        # Если content не передается, то используется значение по умолчанию
        article = Article.objects.create(
            title="Новостная статья",
            summary="Краткое содержание"
        )
        self.assertIn("В статье подробно рассмотрены", article.content)

class GlossaryTermModelTest(TestCase):
    def test_glossary_term_str(self):
        term = GlossaryTerm.objects.create(
            term="ТО",
            definition="Техническое обслуживание автомобиля"
        )
        self.assertEqual(str(term), "ТО")
        self.assertEqual(term.definition, "Техническое обслуживание автомобиля")

class VacancyModelTest(TestCase):
    def test_vacancy_str(self):
        vacancy = Vacancy.objects.create(
            title="Администратор",
            description="Вакансия для администратора компании"
        )
        self.assertEqual(str(vacancy), "Администратор")
        self.assertIn("Вакансия", vacancy.description)

class ContactModelTest(TestCase):
    def test_contact_str(self):
        contact = Contact.objects.create(
            name="Иванов Иван",
            position="Администратор",
            phone="+375 (29) 111-22-33",
            email="ivanov@example.com"
        )
        self.assertEqual(str(contact), "Иванов Иван")
        self.assertEqual(contact.position, "Администратор")

class CompanyInfoModelTest(TestCase):
    def test_company_info_str(self):
        info = CompanyInfo.objects.create(
            description="Информация о компании",
            history="История компании по годам",
            details="Реквизиты компании"
        )
        self.assertEqual(str(info), "Информация о компании")
        self.assertIn("Информация", info.description)

class ReviewModelTest(TestCase):
    def test_review_str(self):
        review = Review.objects.create(
            name="Анонимный пользователь",
            rating=5,
            text="Отличный сервис!"
        )
        self.assertEqual(str(review), "Анонимный пользователь")
        self.assertEqual(review.rating, 5)
