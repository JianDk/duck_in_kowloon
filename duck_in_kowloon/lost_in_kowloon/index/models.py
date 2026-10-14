from django.db import models
from django.core.exceptions import ValidationError


class Dish(models.Model):
	name = models.CharField(max_length=120)
	short_description = models.CharField(max_length=50)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	image = models.ImageField(upload_to="menu/", blank=True, null=True)
	display_order = models.PositiveSmallIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["display_order", "name"]

	def __str__(self):
		return f"{self.name} (DKK {self.price})"

	def clean(self):
		super().clean()
		if not self.is_active:
			return

		active_count = Dish.objects.filter(is_active=True).exclude(pk=self.pk).count()
		if active_count >= 15:
			raise ValidationError("You can only keep up to 15 active dishes.")

	def save(self, *args, **kwargs):
		old_image_name = None
		old_storage = None

		if self.pk:
			try:
				existing = Dish.objects.get(pk=self.pk)
				if existing.image:
					old_image_name = existing.image.name
					old_storage = existing.image.storage
			except Dish.DoesNotExist:
				pass

		self.full_clean()
		saved = super().save(*args, **kwargs)

		new_image_name = self.image.name if self.image else None
		if old_image_name and old_image_name != new_image_name and old_storage:
			old_storage.delete(old_image_name)

		return saved

	def delete(self, *args, **kwargs):
		image_name = self.image.name if self.image else None
		storage = self.image.storage if self.image else None
		deleted = super().delete(*args, **kwargs)

		if image_name and storage:
			storage.delete(image_name)

		return deleted
