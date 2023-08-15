from django.contrib import admin

from eiger.moonboard.models import (
    AccountData,
    Boulder,
    HoldSetup,
    LogbookEntry,
    Move,
)


@admin.register(HoldSetup)
class HoldSetupAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')


@admin.register(Boulder)
class BoulderAdmin(admin.ModelAdmin):
    list_display = ('id', 'hold_setup', 'grade', 'is_benchmark')


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id', 'hold', 'is_start', 'is_end', 'boulder')


@admin.register(AccountData)
class AccountDataAdmin(admin.ModelAdmin):
    ...


@admin.register(LogbookEntry)
class LogbookEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'boulder',
        'date_climbed',
        'comment',
        'attempts',
        'user_grade',
    )
