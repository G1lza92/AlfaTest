import json
from datetime import timedelta

import redis
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

from .models import User

redis_con = redis.Redis('localhost')


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
def get_data(user_id: int):
    """Получение данных о покупках пользователя из внешнего сервиса по ID."""
    url = f'https://my-external-dummy-service.net/api/v1/user/{user_id}/shopping/'
    headers = {'Authorization': settings.TOKEN}
    result = requests.get(url, headers=headers)
    return result.content


class ShoppingAmountAPIView(APIView):
    """Получение суммы покупок пользователя по его логину."""

    def get(self, request, login: str):
        user = get_object_or_404(User, login=login)
        amount = self.get_shopping_amount(user.id)
        return Response(amount)

    def get_shopping_amount(self, user_id: int) -> int:
        redis_key = f'user_data:{user_id}'
        try:
            purchases = get_data(user_id)
        except RetryError:
            cached_data = redis_con.get(redis_key)
            if cached_data:
                external_user_data = json.loads(cached_data)
                return external_user_data['amount']
            else:
                return 0
        external_data = json.loads(purchases)
        amount = sum(data['amount'] for data in external_data)
        external_user_data = {
            'user_id': user_id,
            'response_data': purchases,
            'amount': amount,
        }
        redis_con.setex(
            redis_key,
            timedelta(hours=3),
            json.dumps(external_user_data),
        )
        return amount
