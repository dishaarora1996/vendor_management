from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PurchaseOrder, Vendor
from .serializers import PurchaseOrderSerializer, VendorSerializer
from rest_framework.exceptions import APIException, ValidationError

# Create your views here.



class PurchaseOrderAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
            if serializer.is_valid():
                try:
                    serializer.save()
                except Exception as e:
                    raise APIException({'msg': str(e), 'request_status': 0})
                return Response({"results": serializer.data, 'request_status': 1, "msg": "Successfully updated"}, status=status.HTTP_200_OK)
            raise APIException({'msg': serializer.errors, 'request_status': 0})
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, po_id, format=None):
        purchase_order = PurchaseOrder.cmobjects.filter(pk=po_id).first()
        if purchase_order:
            purchase_order.is_deleted = True
            purchase_order.updated_by = request.user
            purchase_order.save()
            return Response({"results": purchase_order.values(), 'request_status': 1, "msg": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)



class VendorAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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
            serializer = VendorSerializer(vendor, data=request.data)
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
        vendor = Vendor.cmobjects.filter(pk=vendor_id).first()
        if vendor:
            vendor.is_deleted = True
            vendor.updated_by = request.user
            vendor.save()
            return Response({"results": vendor.values(), 'request_status': 1, "msg": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"msg": "Not Found", 'request_status': 0}, status=status.HTTP_404_NOT_FOUND)

