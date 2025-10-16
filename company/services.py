from django.db import transaction
from django.db.models import F
from .models import Order, Holding, InstrumentStats

def place_order(user, company, order_type, quantity, price):
    stats = InstrumentStats.objects.select_for_update().get(company=company)
    if price < stats.band_low or price > stats.band_high:
        raise ValueError("Price outside 5% band")

    if order_type == Order.SELL:
        holding = Holding.objects.select_for_update().get(user=user, company=company)
        if holding.quantity < quantity:
            raise ValueError("Insufficient holdings")

    with transaction.atomic():
        order = Order.objects.create(
            user=user, company=company, type=order_type, quantity=quantity, price=price
        )
        match_orders(order, stats)
        return order

def match_orders(incoming, stats):
    if incoming.type == Order.BUY:
        candidates = (Order.objects
            .select_for_update()
            .filter(company=incoming.company, type=Order.SELL, status=Order.OPEN, price__lte=incoming.price)
            .order_by('price', 'created_at'))
    else:
        candidates = (Order.objects
            .select_for_update()
            .filter(company=incoming.company, type=Order.BUY, status=Order.OPEN, price__gte=incoming.price)
            .order_by('-price', 'created_at'))

    for other in candidates:
        if incoming.remaining == 0:
            break
        if other.remaining == 0:
            continue

        trade_qty = min(incoming.remaining, other.remaining)
        trade_price = other.price if other.created_at <= incoming.created_at else incoming.price

        if not (stats.band_low <= trade_price <= stats.band_high):
            continue

        if incoming.type == Order.BUY:
            Holding.objects.filter(user=incoming.user, company=incoming.company).update(
                quantity=F('quantity') + trade_qty
            )
            Holding.objects.filter(user=other.user, company=other.company).update(
                quantity=F('quantity') - trade_qty
            )
        else:
            Holding.objects.filter(user=other.user, company=other.company).update(
                quantity=F('quantity') + trade_qty
            )
            Holding.objects.filter(user=incoming.user, company=incoming.company).update(
                quantity=F('quantity') - trade_qty
            )

        other.quantity_filled += trade_qty
        incoming.quantity_filled += trade_qty
        if other.remaining == 0:
            other.status = Order.FILLED
        else:
            other.status = Order.PART
        if incoming.remaining == 0:
            incoming.status = Order.FILLED
        else:
            incoming.status = Order.PART
        other.save()
        incoming.save()

        stats.last_price = trade_price
        stats.save()
