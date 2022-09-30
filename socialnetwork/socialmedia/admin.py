from django.contrib import admin
from .models import *

# Specifying viewable editable/noneditable fields of user in admin page


class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'birthDate')

# Specifying viewable editable/noneditable fields of friends in admin page


class FriendAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'chat')
    readonly_fields = ('date',)

# Specifying viewable editable/noneditable fields of status in admin page


class StatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'user')
    readonly_fields = ('date', 'lastDate',)

# Specifying viewable editable/noneditable fields of image in admin page


class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'thumbnail', 'user', 'image_tag')

    # view the image
    readonly_fields = ['image_tag']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ImageAdmin, self).get_form(request, obj, **kwargs)

        # make the thumnail field not required
        form.base_fields['thumbnail'].required = False
        return form


admin.site.register(AppUser, UserAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(UserUserFriend, FriendAdmin)
