from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Mentor, Mentee, Interest, MentorInterest, MenteeInterest

User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'birth_date', 'email', 'is_mentor', 'agreed_to_terms')
    list_filter = ('is_mentor', 'agreed_to_terms')
    search_fields = ('username', 'email', 'name')

class MentorInterestInline(admin.TabularInline):
    model = MentorInterest
    extra = 1

class MentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_interests', 'rating', 'total_ratings')
    search_fields = ('user__username', 'user__name')
    inlines = [MentorInterestInline]

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = "Interests"

class MenteeInterestInline(admin.TabularInline):
    model = MenteeInterest
    extra = 1

class MenteeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_interests')
    search_fields = ('user__username', 'user__name')
    inlines = [MenteeInterestInline]

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = "Interests"

class InterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Interest, InterestAdmin)