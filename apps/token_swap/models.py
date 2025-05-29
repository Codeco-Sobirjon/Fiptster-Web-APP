import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenSwap(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_swaps', verbose_name='User')
	amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='Amount from FIPTp')
	total_exchange = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='Total FIPT Exchange')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Token Swap'
		verbose_name_plural = 'Token Swaps'

	def __str__(self):
		return f"{self.user.username} - {self.total_exchange} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
