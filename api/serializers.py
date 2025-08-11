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
    
    # product = ProductSerializer()
    # This line gives nested serializer info of product but i want customized data i go for below
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price',max_digits=10,decimal_places=2)
    
    class Meta:
        model = OrderItem
        # fields = (
        #     'product',
        #     'quantity',
        # ) 
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal',
        )   
        
class OrderSerializer(serializers.ModelSerializer):
    '''
    It is Nested Serializer, it is useful for nested lists if we doesn't need all the data then coment this it only shows primary key rel...
    '''
    # items = OrderItemSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')
    
    def total(self,obj):
        order_items = obj.items.all()
        return sum(item.item_subtotal for item in order_items)   
    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'created_at',
            'status',
            'items',
            'total_price',
        )
             
        
    
