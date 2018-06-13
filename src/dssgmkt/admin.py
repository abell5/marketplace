from django.contrib import admin
# from .models import Skill, Organization, Project, ProjectLog, ProjectFollower, ProjectTask, \
# ProjectTaskReview, ProjectTaskRequirement, VolunteerApplication, User, VolunteerProfile, \
# VolunteerSkill, OrganizationMembershipRequest, OrganizationRole, ProjectRole, ProjectTaskRole


from .models import org, proj, user

admin.site.register(user.Skill)
admin.site.register(org.Organization)
admin.site.register(proj.Project)
admin.site.register(proj.ProjectLog)
admin.site.register(proj.ProjectFollower)
admin.site.register(proj.ProjectTask)
admin.site.register(proj.ProjectTaskReview)
admin.site.register(proj.ProjectTaskRequirement)
admin.site.register(proj.VolunteerApplication)
admin.site.register(user.User)
admin.site.register(user.VolunteerProfile)
admin.site.register(user.VolunteerSkill)
admin.site.register(org.OrganizationMembershipRequest)
admin.site.register(org.OrganizationRole)
admin.site.register(proj.ProjectRole)
admin.site.register(proj.ProjectTaskRole)
