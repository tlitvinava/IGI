import os
import django
import matplotlib.pyplot as plt
from django.db.models import Count

# Настроим окружение Django: укажите путь к файлу настроек вашего проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_project.settings")
django.setup()

from autoservice.models import Order

# Получаем данные: для каждой услуги считаем количество заказов
orders_data = Order.objects.values('service__name').annotate(order_count=Count('id')).order_by('service__name')

# Если у какого-то заказа не указана услуга, обозначим как "Без услуги"
services = [entry['service__name'] if entry['service__name'] is not None else "Без услуги" for entry in orders_data]
order_counts = [entry['order_count'] for entry in orders_data]

# Построение столбчатой диаграммы
plt.figure(figsize=(10, 6))
plt.bar(services, order_counts, color='skyblue')
plt.xlabel('Услуга')
plt.ylabel('Количество заказов')
plt.title('Количество заказов по услугам')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Сохраняем график в файл
output_file = os.path.join(os.getcwd(), "orders_per_service.png")
plt.savefig(output_file)
plt.close()

print(f"График успешно сохранён в файл: {output_file}")
