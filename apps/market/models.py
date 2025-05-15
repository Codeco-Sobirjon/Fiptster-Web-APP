import uuid
from django.db import models
from multiselectfield import MultiSelectField


class Category(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Название категории')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = '1. Категория'
		verbose_name_plural = '1. Категории'


class Market(models.Model):
	class SizeType(models.TextChoices):
		first_choice = 'XS', 'XS'
		second_choice = 'S', 'S'
		third_choice = 'M', 'M'
		fourth_choice = 'L', 'L'
		fifth_choice = 'XL', 'XL'
		sixth_choice = 'XXL', 'XXL'

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Название товара')
	price_fiptp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена в FIPTP')
	price_dollor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена в долларах')
	image = models.ImageField(upload_to='market/', verbose_name='Изображение')
	sizes = MultiSelectField(choices=SizeType.choices, verbose_name='Размеры', null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = '2. Товар'
		verbose_name_plural = '2. Товары'


class Order(models.Model):
	class SizeType(models.TextChoices):
		first_choice = 'XS', 'XS'
		second_choice = 'S', 'S'
		third_choice = 'M', 'M'
		fourth_choice = 'L', 'L'
		fifth_choice = 'XL', 'XL'
		sixth_choice = 'XXL', 'XXL'

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='orders',
	                         verbose_name='Пользователь',
	                         null=True, blank=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='orders', verbose_name='Товар')
	sizes = MultiSelectField(choices=SizeType.choices, verbose_name='Размеры')
	full_name = models.CharField(max_length=255, verbose_name='ФИО')
	email = models.EmailField(verbose_name='Email')
	address = models.CharField(max_length=255, verbose_name='Адрес')
	city = models.CharField(max_length=255, verbose_name='Город')
	country = models.CharField(max_length=255, verbose_name='Страна')
	zip_code = models.CharField(max_length=20, verbose_name='Почтовый индекс')
	is_shipping = models.BooleanField(default=False, verbose_name='Доставка')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = '3. Заказ'
		verbose_name_plural = '3. Заказы'
