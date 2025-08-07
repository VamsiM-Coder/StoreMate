# from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from api.serializers import ProductSerializer, OrderSerializer
from api.models import Product,Order
from rest_framework.response import Response
from rest_framework.decorators import api_view

#Plain Django :  JSON only
'''
def product_list(request):
    products = Product.objects.all()
    serialized = ProductSerializer(products,many=True)
    return JsonResponse ({
        'data' : serialized.data
    })  
'''

#DRF: It is DjangoRestFrameworkBrowsableAPI : By this we can see different HTTP methods like api view, json view
#Getting all products
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serialized = ProductSerializer(products,many=True)
    return Response(serialized.data)    

#Get data by using primary key(id)
@api_view(['GET'])
def product_detail(request,pk):
    product = get_object_or_404(Product,pk=pk)
    serialized = ProductSerializer(product)
    return Response(serialized.data)

@api_view(['GET'])
def order_list(request):
    orders = Order.objects.all()
    serialized = OrderSerializer(orders,many=True)
    return Response(serialized.data)

