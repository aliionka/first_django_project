from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "created_at",
            "price",
            "discount",
            "archived",
            "preview",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "pk",
            "order_date",
            "user",
            "products",
            "address",
            "promocode",
            "comment",
        )
