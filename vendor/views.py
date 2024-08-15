from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PurchaseOrder, Vendor
from .serializers import PurchaseOrderSerializer, VendorSerializer, RegisterSerializer
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.authtoken.models import Token
from vendor import models
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.



class PurchaseOrderAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, po_id=None, format=None):
        if po_id:
            purchase_order = PurchaseOrder.cmobjects.filter(pk=po_id).first()
            if purchase_order:
                serializer = PurchaseOrderSerializer(purchase_order)
                return Response({"results": serializer.data, 'request_status': 1}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)
        else:
            vendor_id = request.query_params.get('vendor')
            queryset = PurchaseOrder.cmobjects.all()
            if vendor_id:
                queryset = queryset.filter(vendor_id=vendor_id)
            serializer = PurchaseOrderSerializer(queryset, many=True)
            return Response({"results": serializer.data, 'request_status': 1}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                raise APIException({'msg': str(e), 'request_status': 0})
            return Response({"results": serializer.data, 'request_status': 1, "msg": "Successfully created"}, status=status.HTTP_200_OK)
        raise APIException({'msg': serializer.errors, 'request_status': 0})

    def put(self, request, po_id, format=None):
        purchase_order = PurchaseOrder.cmobjects.filter(pk=po_id).first()
        if purchase_order:
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    purchase_order = serializer.save()
                    # purchase_order.updated_by = request.user
                    # purchase_order.save()

                except Exception as e:
                    raise APIException({'msg': str(e), 'request_status': 0})
                return Response({"results": serializer.data, 'request_status': 1, "msg": "Successfully updated"}, status=status.HTTP_200_OK)
            raise APIException({'msg': serializer.errors, 'request_status': 0})
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, po_id, format=None):
        purchase_order = PurchaseOrder.cmobjects.filter(pk=po_id)
        purchase_order_obj = purchase_order.first()
        purchase_order_value = purchase_order.values().first()
        if purchase_order_obj:
            purchase_order_obj.is_deleted = True
            purchase_order_obj.updated_by = request.user
            purchase_order_obj.save()
            return Response({"results": purchase_order_value, 'request_status': 1, "msg": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)



class VendorAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id=None, format=None):
        if vendor_id:
            vendor = Vendor.cmobjects.filter(pk=vendor_id).first()
            if vendor:
                serializer = VendorSerializer(vendor)
                return Response({"results": serializer.data, 'request_status': 1}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)
        else:
            vendor = Vendor.cmobjects.all()
            serializer = VendorSerializer(vendor, many=True)
            return Response({"results": serializer.data, 'request_status': 1}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = VendorSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                raise APIException({'msg': str(e), 'request_status': 0})
            return Response({"results": serializer.data, 'request_status': 1, "msg": "Successfully created"}, status=status.HTTP_200_OK)
        raise APIException({'msg': serializer.errors, 'request_status': 0})

    def put(self, request, vendor_id, format=None):
        vendor = Vendor.cmobjects.filter(pk=vendor_id).first()
        if vendor:
            serializer = VendorSerializer(vendor, data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    serializer.save()
                except Exception as e:
                    raise APIException({'msg': str(e), 'request_status': 0})
                return Response({"results": serializer.data, 'request_status': 1, "msg": "Successfully updated"}, status=status.HTTP_200_OK)
            raise APIException({'msg': serializer.errors, 'request_status': 0})
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, vendor_id, format=None):
        vendor = Vendor.cmobjects.filter(pk=vendor_id)
        vendor_obj = vendor.first()
        vendor_value = vendor.values().first()
        if vendor_obj:
            vendor_obj.is_deleted = True
            vendor_obj.updated_by = request.user
            vendor_obj.save()
            return Response({"results": vendor_value, 'request_status': 1, "msg": "Successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)


class RegisterAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except Exception as e:
                raise APIException({'msg': str(e), 'request_status': 0})
            token, created = Token.objects.get_or_create(user=user)
            data = {
                    "username": user.username,
                    "email": user.email,
                    "token": token.key,
                    'request_status': 1,
                    "msg": "Successfully registered"

                }
            return Response(data, status=status.HTTP_201_CREATED)
        raise APIException({'msg': serializer.errors, 'request_status': 0})

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is None:
            raise APIException({'msg': 'Invalid username or password', 'request_status': 0})

        # Create or get the token for the user
        token, created = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'request_status': 1,
            "msg": "Successfully login"
        }
        return Response(data, status=status.HTTP_200_OK)
