import uuid
from django.db import models
from multiselectfield import MultiSelectField


class Category(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Category Name')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = '1. Category'
		verbose_name_plural = '1. Categories'


class Market(models.Model):
	class SizeType(models.TextChoices):
		first_choice = 'XS', 'XS'
		second_choice = 'S', 'S'
		third_choice = 'M', 'M'
		fourth_choice = 'L', 'L'
		fifth_choice = 'XL', 'XL'
		sixth_choice = 'XXL', 'XXL'

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Product Name')
	price_fiptp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price (FIPTP)')
	price_dollor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price (USD)')
	image = models.ImageField(upload_to='market/', verbose_name='Image')
	sizes = MultiSelectField(choices=SizeType.choices, verbose_name='Sizes', null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = '2. Product'
		verbose_name_plural = '2. Products'


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
	                         verbose_name='User', null=True, blank=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='orders', verbose_name='Product')
	sizes = MultiSelectField(choices=SizeType.choices, verbose_name='Sizes')
	full_name = models.CharField(max_length=255, verbose_name='Full Name')
	email = models.EmailField(verbose_name='Email')
	address = models.CharField(max_length=255, verbose_name='Address')
	city = models.CharField(max_length=255, verbose_name='City')
	country = models.CharField(max_length=255, verbose_name='Country')
	zip_code = models.CharField(max_length=20, verbose_name='Postal Code')
	is_shipping = models.BooleanField(default=False, verbose_name='Shipping')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = '3. Order'
		verbose_name_plural = '3. Orders'
