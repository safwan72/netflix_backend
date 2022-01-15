from django.shortcuts import render
from rest_framework.views import APIView
from stripe.api_resources import source
from . import models, serializers
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from django.conf import settings


class UserCreateSerializerView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer


def create(self, request, *args, **kwargs):
    serializer = serializers.UserSerializer(data=request.data)

    if serializer.is_valid():
        self.perform_create(serializer)
        return Response(serializer.data.tokens, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPlanSerializerView(generics.RetrieveAPIView):
    queryset = models.UserPlans.objects.all()
    serializer_class = serializers.UserPlanSerializer
    lookup_field = "user__id"


class UserProfileSerializerView(generics.RetrieveUpdateAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileUpdateSerializer
    lookup_field = "user__id"

    def patch(self, request, *args, **kwargs):
        userID = kwargs["user__id"]
        data = request.data
        user_profile = models.UserProfile.objects.get(id=userID)
        user_profile.first_name = data.get(
            "first_name", user_profile.first_name)
        user_profile.last_name = data.get("last_name", user_profile.last_name)
        user_profile.username = data.get("username", user_profile.username)
        user_profile.profile_pic = request.FILES.get(
            "profile_pic", user_profile.profile_pic
        )
        user_profile.phone = data.get("phone", user_profile.phone)
        user_profile.address = data.get("address", user_profile.address)
        user_profile.save()
        user_profile_serializer = serializers.UserProfileUpdateSerializer(
            user_profile, context={"request": request}
        )
        return Response(user_profile_serializer.data)
        # return self.update(request, *args, **kwargs)


class MyTokenObtainPairView(TokenObtainPairView, mixins.RetrieveModelMixin):
    serializer_class = serializers.MyTokenObtainPairSerializer


class PlansView(generics.ListAPIView):
    serializer_class = serializers.PlanSerializer
    queryset = models.Plans.objects.all()


stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["POST"])
def test_payment(request):
    data = request.data
    token = data.get("token")
    address = data.get("addresses")
    u_id = data.get("u_id")
    plan = data.get("selectedplan")
    amount = plan['amount']
    total = int(round(amount*100, 2))
    errormsg = ''
    try:
        charge = stripe.Charge.create(
            amount=total,
            currency="usd",
            source=token['id']
        )

    except stripe.error.CardError as e:
        errormsg(e)
    except stripe.error.RateLimitError as e:
        errormsg(e)
        # Too many requests made to the API too quickly
    except stripe.error.InvalidRequestError as e:
        errormsg(e)
        # Invalid parameters were supplied to Stripe API
    except stripe.error.AuthenticationError as e:
        print(e)
        # Authentication Error: Authentication with Stripe API failed (maybe you changed API keys recently)

    except stripe.error.APIConnectionError as e:
        errormsg(e)
        # Network communication with Stripe failed

    except stripe.error.StripeError as e:
        errormsg(e)
        # Stripe Error

    else:
        # success
        user = models.User.objects.get(id=u_id)
        userprofile = models.UserProfile.objects.get(user=user)
        plan = models.Plans.objects.get(plan_id=plan['plan_id'])
        if user:
            userplan, created = models.UserPlans.objects.get_or_create(
                user=userprofile)
            userplan.plan = plan
            userplan.paid = True
            address_user = address['billing_address_line1'] + \
                address['billing_address_city'] + \
                address['billing_address_country']
            userplan.billing_email = token['email']
            userplan.billing_address = address_user
            userplan.save()
            errormsg = False
    return Response(status=status.HTTP_200_OK, data={
        "error": errormsg,
    })
