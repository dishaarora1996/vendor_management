from rest_framework import serializers
from .models import *
from datetime import datetime



class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = "__all__"
        read_only_fields = ['vendor_code', 'created_by', 'updated_by']

    def create(self, validated_data):

        request = self.context.get('request')

        # Generate a unique vendor_code based on the current timestamp
        new_vendor_code = datetime.now().strftime("VN-%Y%m%d%H%M%S")
        validated_data['vendor_code'] = new_vendor_code
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user

        # Create the Vendor instance without using super()
        vendor = Vendor.objects.create(**validated_data)

        return vendor

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.updated_by = request.user  # Set updated_by to the current user

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PurchaseOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = ['po_number', 'created_by', 'updated_by']

    def update_fulfillment_rate(self, instance):

        # Calculate total POs and successfully fulfilled POs
        total_pos = PurchaseOrder.objects.filter(vendor=instance.vendor).count()
        fulfilled_pos = PurchaseOrder.objects.filter(
            vendor=instance.vendor,
            status='completed'
        ).count()
        print("total_pos", total_pos)
        print("fulfilled_pos", fulfilled_pos)
        # Calculate fulfillment rate
        fulfillment_rate = round((fulfilled_pos / total_pos) * 100, 2) if total_pos > 0 else 0.0
        print("fulfillment_rate", fulfillment_rate)
        print(" instance.vendor",  instance.vendor)
        instance.vendor.fulfillment_rate = fulfillment_rate
        instance.vendor.save(update_fields=['fulfillment_rate'])

        print(" instance.vendor.fulfillment_rate",  instance.vendor.fulfillment_rate)

    def create(self, validated_data):
        request = self.context.get('request')
        # Find the last PurchaseOrder and increment the last po_number
        last_order = PurchaseOrder.objects.all().order_by('id').last()
        if last_order:
            last_po_number = int(last_order.po_number.split('-')[-1])
            new_po_number = f"PO-{str(last_po_number + 1).zfill(4)}"
        else:
            new_po_number = "PO-0001"

        validated_data['po_number'] = new_po_number
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user

        purchase_order = PurchaseOrder.objects.create(**validated_data)

        return purchase_order

    def update(self, instance, validated_data):

        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context.get('request')
        instance.updated_by = request.user
        instance.save()

        if new_status != old_status:
            self.update_fulfillment_rate(instance)

        # Log status before and after update
        print("Old Status in Serializer:", old_status)
        print("New Status in Serializer:", new_status)

        return instance



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def create(self, validated_data):
        # Extracting the passwords
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')

        # Checking if the two passwords match
        if password != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Checking if email already exists
        if User.objects.filter(email=validated_data["email"]).exists():
            raise serializers.ValidationError({"password": "Email laready exists."})

        # Creating the user
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(password)
        user.save()

        return user




