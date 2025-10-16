from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Order, Company
from .serializers import OrderSerializer
from .services import place_order

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = get_object_or_404(Company, id=serializer.validated_data['company'].id)
        order_type = serializer.validated_data['type']
        quantity = serializer.validated_data['quantity']
        price = serializer.validated_data['price']

        try:
            order = place_order(
                user=request.user,
                company=company,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
