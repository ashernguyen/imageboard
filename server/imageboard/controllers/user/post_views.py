from django.db.models import F
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from datetime import datetime, timedelta

from ... import models
from ... import constants
from ...utils import get_visitor_ip, PasswordUtils, StringUtils

# Helpers

def is_user_authorized(ip):
    token = models.UserToken.objects.filter(ip=ip)
    if len(token) == 0:
        return False
    token = token[0]

    user = models.User.objects.filter(token=token)[0]
    return user.is_authorized()

def does_user_exist(name_email):
    user = models.User.objects.filter(Q(name=name_email) | Q(email=name_email))
    if len(user) == 0:
        return False
    else:
        return True

def is_password_correct(name_email, password):
    user = models.User.objects.filter(Q(name=name_email) | Q(email=name_email))[0]
    algo_crypt, algo_string = user.pass_algo.split('+')
    pass_hash = PasswordUtils.get_hash_pass(algo_crypt, algo_string, password, user.pass_salt)
    return pass_hash == user.pass_hash

# Views

def authorize(request, *args, **kwargs):
    if request.method == 'POST':
        ip = kwargs.get('ip', get_visitor_ip(request))
        if is_user_authorized(ip):
            message = {
                'message' : 'User already authorized.'
            }
            return Response(message, status=status.HTTP_304_NOT_MODIFIED, content_type='application/json')
        
        name_email = request.data.get('username')
        if not does_user_exist(name_email):
            message = {
                'message' : 'This user doesn\'t exist.'
            }
            return Response(message, status=status.HTTP_404_NOT_FOUND, content_type='application/json')

        password = request.data.get('password')
        if not is_password_correct(name_email, password):
            message = {
                'message' : 'Incorrect password.'
            }
            return Response(message, status=status.HTTP_403_FORBIDDEN, content_type='application/json')

        user_token = models.UserToken.objects.create(**{
            'value' : StringUtils.random(200),
            'expired_at' : datetime.now() + timedelta(days=constants.EXPIRATION_DAYS),
            'ip' : ip
        })
        user = models.User.objects.filter(Q(name=name_email) | Q(email=name_email))[0]
        user.token = user_token
        user.save()

        data = {
            'token' : user.token.value,
            'expired_at' : user.token.expired_at.strftime('%d/%m/%Y %H:%M:%S')
        }
        return Response(data, status=status.HTTP_200_OK, content_type='application/json')
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
