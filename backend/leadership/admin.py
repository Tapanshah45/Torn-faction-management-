from django.contrib import admin

from .models import (
    ChainAssignment,
    ChainBreakEvent,
    PayoutCalculation,
    PayoutDistribution,
    RankedWarPayout,
    RankedWarPayoutMember,
    ReliabilityScore,
)

admin.site.register(PayoutCalculation)
admin.site.register(PayoutDistribution)
admin.site.register(RankedWarPayout)
admin.site.register(RankedWarPayoutMember)
admin.site.register(ChainAssignment)
admin.site.register(ChainBreakEvent)
admin.site.register(ReliabilityScore)
