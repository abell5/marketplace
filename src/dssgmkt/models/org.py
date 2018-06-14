from django.db import models
from django_countries.fields import CountryField
from dssgsolve import settings

from .common import (PHONE_REGEX, MAIN_CAUSE_CHOICES, CAUSE_EDUCATION,
                            ORGANIZATION_ROLE_CHOICES, ROLE_ORGANIZATION_STAFF,
                            REVIEW_RESULT_CHOICES, REVIEW_NEW)


class Organization(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Organization name",
        help_text="Type the name of your organization.",
    )
    description = models.TextField(
        max_length=5000,
        verbose_name="Organization description",
        help_text="Write a description for volunteers to understand the context of your projects.",
    )
    logo_url = models.URLField(
        verbose_name="Organization logo",
        help_text="Upload an image file that represents your organization",
        blank=True,
        null=True,
    )
    website_url = models.URLField(
        verbose_name="External website URL",
        help_text="Add a link to your organization's home page so volunteers can reach you",
        max_length=200,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        verbose_name="Phone number",
        validators=[PHONE_REGEX],
        max_length=17,
        blank=True,
        null=True,
    )
    email_address = models.EmailField(
        verbose_name="Contact email",
        blank=True,
        null=True,
    )
    street_address = models.CharField(
        verbose_name="Address line 1",
        max_length=300,
    )
    address_line_2 = models.CharField(
        verbose_name="Address line 2",
        max_length=300,
        blank=True,
        null=True,
    )
    city = models.CharField(
        verbose_name="City",
        max_length=100,
    )
    state = models.CharField(
        verbose_name="State/Province",
        max_length=100,
    )
    zipcode = models.CharField(
        verbose_name="ZIP/Postal code",
        max_length=20,
    )
    country = CountryField(verbose_name="Country")

    class Budget():
        B100K = 'B000'
        B500K = 'B001'
        B1M = 'B005'
        B5M = 'B010'
        B20M = 'B050'
        B50M = 'B200'
        B50MP = 'B500'

    BUDGET_CHOICES = (
        (Budget.B100K, '<$100K'),
        (Budget.B500K, '$100K-$500K'),
        (Budget.B1M, '$500K-$1MM'),
        (Budget.B5M, '$1MM-$5MM'),
        (Budget.B20M, '$5MM-$20MM'),
        (Budget.B50M, '$20MM-$50MM'),
        (Budget.B50MP, '>$50MM')
    )
    budget = models.CharField(
        verbose_name="Yearly budget",
        help_text="Select the budget range that fits your organization best",
        max_length=7,
        choices=BUDGET_CHOICES,
        default=Budget.B100K,
    )

    class YearsInOperation():
        Y0 = 'Y00'
        Y1 = 'Y01'
        Y5 = 'Y05'
        Y10 = 'Y10'
        Y25 = 'Y25'

    OPERATION_YEARS_CHOICES = (
        (YearsInOperation.Y0, 'less than 1 year'),
        (YearsInOperation.Y1, '1 to 5 years'),
        (YearsInOperation.Y5, '5 to 10 years'),
        (YearsInOperation.Y10, '10 to 25 years'),
        (YearsInOperation.Y25, '25 or more years')
    )
    years_operation = models.CharField(
        verbose_name="Years in operation",
        help_text="For how long has the organization been in operation?",
        max_length=3,
        choices=OPERATION_YEARS_CHOICES,
        default=YearsInOperation.Y0,
    )
    main_cause = models.CharField(
        verbose_name="Main social cause",
        help_text="What is the main social cause that this organization has as a goal?",
        max_length=2,
        choices=MAIN_CAUSE_CHOICES,
        default=CAUSE_EDUCATION,
    )

    class GeographicalScope():
        LOCAL = 'LO'
        STATE = 'ST'
        REGION = 'RE'
        COUNTRY = 'CO'
        MULTINATIONAL = 'MN'
        OTHER = 'OT'
        
    ORGANIZATION_SCOPE_CHOICES = (
        (GeographicalScope.LOCAL, 'City/Local'),
        (GeographicalScope.STATE, 'State'),
        (GeographicalScope.REGION, 'Region (i.e. Midwest, Northeast, etc.)'),
        (GeographicalScope.COUNTRY, 'Country'),
        (GeographicalScope.MULTINATIONAL, 'Multi-national'),
        (GeographicalScope.OTHER, 'Other')
    )
    organization_scope = models.CharField(
        verbose_name="Geographical scope",
        help_text="What is the geographical scope that this organization targets?",
        max_length=2,
        choices=ORGANIZATION_SCOPE_CHOICES,
        default=GeographicalScope.LOCAL,
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now= True)

    def __str__(self):
        return self.name

class OrganizationMembershipRequest(models.Model):
    role = models.IntegerField(choices = ORGANIZATION_ROLE_CHOICES, default=ROLE_ORGANIZATION_STAFF)
    status = models.CharField(max_length=3, choices=REVIEW_RESULT_CHOICES, default=REVIEW_NEW)
    public_reviewer_comments = models.TextField(max_length=5000, blank=True, null=True)
    private_reviewer_notes = models.TextField(max_length=5000, blank=True, null=True)
    request_date = models.DateTimeField(auto_now_add=True)
    resolution_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def is_new(self):
        return self.status == REVIEW_NEW

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == ACCEPTED and not self.user.is_organization_member(self.organization):
            new_role = OrganizationRole(role = self.role, user = self.user, organization = self.organization)
            new_role.save()
## TODO move this to the logic in the views?

class OrganizationRole(models.Model):
    role = models.IntegerField(choices = ORGANIZATION_ROLE_CHOICES, default=ROLE_ORGANIZATION_STAFF)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user','organization')
