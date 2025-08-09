from rest_framework import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'desc',
            'price',
            'stock',
        )
        
        #or
        # fields = ['name','price', 'stock']
    def validate_price(self,value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value   
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'product',
            'quantity',
        )    
        
class OrderSerializer(serializers.ModelSerializer):
    '''
    It is Nested Serializer, it is useful for nested lists if we doesn't need all the data then coment this...
    '''
    # items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'created_at',
            'status',
            'items',
        )
             
        
    
