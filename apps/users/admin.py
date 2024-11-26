from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    # ordering = ('-date_joined', )
    search_fields = ('email',)
    # list_filter = ('singpass_profile', 'is_cabbies_user', 'fms_onboard_status' )



admin.site.register(User, UserAdmin)
