import pytz
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound

from .models import User
from .utils import AccountActivationTokenGenerator, check_user_validity
from apps.common.constants import (FRONTEND_RESET_PASSWORD_PATH)


class UserListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    nric_number = serializers.CharField(source='profile.nric_number')
    address = serializers.CharField(source='profile.address_1')
    dda_reference = serializers.CharField(source='profile.dda_reference')
    dda_status = serializers.CharField(source='profile.dda_status')
    ownersip = serializers.CharField(source='vehicleinformation.get_ownership_type_display')
    document_count = serializers.IntegerField()
    pdvl = serializers.CharField(source='licenseinformation.type_of_vocational')
    profile_document = serializers.SerializerMethodField()

    percentage_completed = serializers.SerializerMethodField()
    submitted_date = serializers.DateTimeField(source='application_submit_at', format='%d/%m/%Y %I:%M %p',
                                               default_timezone=pytz.timezone('Asia/Singapore'))
    status = serializers.CharField(source='fms_onboard_status')
    account_creation_date = serializers.DateTimeField(source='date_joined', format='%d/%m/%Y %I:%M %p',
                                               default_timezone=pytz.timezone('Asia/Singapore'))
    account_approve_date = serializers.DateTimeField(source='approve_date', format='%d/%m/%Y %I:%M %p',
                                               default_timezone=pytz.timezone('Asia/Singapore'))
    
    # TODO: Need to update after finishing Singpass integration
    data_source = serializers.CharField(default='Singpass')

    def get_profile_document(self, obj):
        if obj.profile_document != []:
            return obj.profile_document[0].upload.url
        return None

    def get_percentage_completed(self, obj):
        return self.context.get('progress_details', dict()).get(obj.id, dict()).get('percentage_completed')

    def to_internal_value(self, value):
        if value.get('nric_number', None) and '****' in value['nric_number']:
            if getattr(self.instance, 'profile', None):
                value['nric_number'] = self.instance.profile.nric_number
        value = super(UserListSerializer, self).to_internal_value(value)
        return value

    def to_representation(self, instance):
        data = super(UserListSerializer, self).to_representation(instance)
        if self.context['request'].user.id != self.context.get('view').kwargs.get('user_id'):
            if getattr(instance, 'profile', None):
                data['nric_number'] = instance.profile.masked_nric_number
                data['dda_reference'] = instance.profile.masked_dda_reference
                data['dda_status'] = instance.profile.cabbies_dda_status  if settings.IS_CABBIES_PORTAL else instance.profile.dda_status
        return data

    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'name', 'nric_number', 'address','dda_status',
                  'dda_reference', 'pdvl', 'ownersip', 'percentage_completed', 'submitted_date',
                  'document_count', 'data_source', 'status', 'singpass_profile', 'profile_document',
                  'account_creation_date','account_approve_date')


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name= validated_data['first_name'],
            last_name= validated_data['last_name'],
            is_active=False,
            email_verified=False,
           
        )
        return user

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        

class VerifyEmailSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        validated_attrs = super(VerifyEmailSerializer, self).validate(attrs)
        uidb64 = validated_attrs.get('uidb64')
        token = validated_attrs.get('token')

        user = User.objects.get_user_with_uidb64(uidb64)
        if not user:
            raise NotFound(_('User not found.'))

        if not AccountActivationTokenGenerator().check_token(user, token):
            raise AuthenticationFailed(('Token is not valid.'))

        user.is_active = True
        user.email_verified = True
        user.save()

        return {
            'message': _('Email verified successfully.')
        }


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = self.context.get('user')
        if not user.is_authenticated:
            validated_attrs = super(RequestPasswordResetSerializer, self).validate(attrs)
            user_email = validated_attrs.get('email')
            user = self._get_user(user_email)

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        relative_link = f'{FRONTEND_RESET_PASSWORD_PATH}?uidb64={uidb64}&token={token}'
        password_reset_link = f'{settings.FRONTEND_URL}{relative_link}'

        return {
            'user': user,
            'password_reset_link': password_reset_link
        }

    def _get_user(self, user_email):
        try:
            user = User.objects.get_by_natural_key(user_email)
        except User.DoesNotExist:
            raise
        check_user_validity(user)
        return user


class VerifyPasswordResetTokenSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        validated_attrs = super(VerifyPasswordResetTokenSerializer, self).validate(attrs)
        uidb64 = validated_attrs.get('uidb64')
        token = validated_attrs.get('token')

        user = User.objects.get_user_with_uidb64(uidb64)
        if not user:
            raise NotFound(_('User not found.'))

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed(('Token is not valid.'))
        validated_attrs['is_valid'] = True
        return validated_attrs


class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        validated_attrs = super(SetNewPasswordSerializer, self).validate(attrs)
        password = validated_attrs.get('password')
        uidb64 = validated_attrs.get('uidb64')
        token = validated_attrs.get('token')

        user = User.objects.get_user_with_uidb64(uidb64)

        if not user:
            raise NotFound(('User not found.'))

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed(('Token is not valid.'))

        password_validation.validate_password(password, user)
        user.set_password(password)
        user.save()

        return {
            'message': _('Password updated successfully.')
        }