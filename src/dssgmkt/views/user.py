from datetime import date

from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rules.contrib.views import (
    PermissionRequiredMixin, objectgetter, permission_required,
)

from ..models.proj import Project, ProjectStatus, ProjectTask
from ..models.user import Skill, User, VolunteerProfile, VolunteerSkill
from .common import build_breadcrumb, home_link


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('dssgmkt:home'))
    # Redirect to a success page.


def my_user_profile_view(request):
    return HttpResponseRedirect(reverse('dssgmkt:user_profile', args=[request.user.id]))

class UserProfileView(generic.DetailView):
    model = User
    pk_url_kwarg = 'user_pk'
    template_name = 'dssgmkt/user_profile.html'
    context_object_name = 'userprofile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = build_breadcrumb([home_link(),
                                                  ("My profile" , None)])

        project_tasks_page_size = 1
        project_tasks = ProjectTask.objects.filter(projecttaskrole__user=self.object.id).filter(~Q(project__status = ProjectStatus.DRAFT)) # TODO create a proxy model for active projects
        project_tasks_paginator = Paginator(project_tasks, project_tasks_page_size)
        project_tasks_page = project_tasks_paginator.get_page(self.request.GET.get('project_tasks_page', 1))
        context['project_tasks'] = project_tasks_page

        return context

class UserProfileEdit(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'skype_name' ]
    template_name = 'dssgmkt/user_profile_edit.html'
    pk_url_kwarg = 'user_pk'

    def get_success_url(self):
        return reverse('dssgmkt:user_profile', args=[self.kwargs['user_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userprofile = get_object_or_404(User, pk=self.kwargs['user_pk'])
        context['userprofile'] = userprofile
        context['breadcrumb'] = build_breadcrumb([home_link(),
                                                  ("My profile" , reverse('dssgmkt:user_profile', args=[userprofile.id])),
                                                  ("Edit profile", None)])
        return context

class VolunteerProfileEdit(UpdateView):
    model = VolunteerProfile
    fields = ['portfolio_url', 'github_url', 'linkedin_url', 'degree_name', 'degree_level',
              'university', 'cover_letter', 'weekly_availability_hours', 'availability_start_date',
              'availability_end_date']
    template_name = 'dssgmkt/user_volunteer_profile_edit.html'
    pk_url_kwarg = 'volunteer_pk'

    def get_success_url(self):
        return reverse('dssgmkt:user_profile', args=[self.kwargs['user_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteerprofile = self.object
        if volunteerprofile and volunteerprofile.user.id == self.request.user.id and self.request.user.id == self.kwargs['user_pk']:
            context['volunteerprofile'] = volunteerprofile
            context['breadcrumb'] = build_breadcrumb([home_link(),
                                                      ("My profile" , reverse('dssgmkt:user_profile', args=[volunteerprofile.user.id])),
                                                      ("Edit volunteer information", None)])
            return context
        else:
            raise Http404

class CreateSkillForm(ModelForm):
    class Meta:
        model = VolunteerSkill
        fields = ['skill', 'level']

def user_profile_skills_edit_view(request, user_pk):
    if request.method == 'GET':
        volunteerskills = VolunteerSkill.objects.filter(user__id = user_pk)

        return render(request, 'dssgmkt/user_profile_skills_edit.html',
                            {'volunteerskills': volunteerskills,
                            'breadcrumb': build_breadcrumb([home_link(),
                                                              ("My profile" , reverse('dssgmkt:user_profile', args=[user_pk])),
                                                              ("Edit skills", None)]),

                            'add_skill_form': CreateSkillForm(),
                            })
    ## TODO this is a security hole as anybody can post to this view and create new skills
    elif request.method == 'POST':
        form = CreateSkillForm(request.POST)
        if form.is_valid:
            skill = form.save(commit = False)
            skill.user = request.user
            skill.save()
            return redirect('dssgmkt:user_profile_skills_edit', user_pk = user_pk)

class VolunteerSkillEdit(UpdateView):
    model = VolunteerSkill
    fields = ['level']
    template_name = 'dssgmkt/user_profile_skills_skill_edit.html'
    pk_url_kwarg = 'skill_pk'

    def get_success_url(self):
        return reverse('dssgmkt:user_profile_skills_edit', args=[self.object.user.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteer_skill = self.object
        if volunteer_skill and volunteer_skill.user.id == self.request.user.id and self.request.user.id == self.kwargs['user_pk']:
            context['volunteerskill'] = volunteer_skill
            context['breadcrumb'] =  build_breadcrumb([home_link(),
                                                      ("My profile" , reverse('dssgmkt:user_profile', args=[self.kwargs['user_pk']])),
                                                      ("Edit skills", reverse('dssgmkt:user_profile_skills_edit', args=[self.kwargs['user_pk']])),
                                                      ("Edit skill", None)])
            return context
        else:
            raise Http404

class VolunteerSkillRemove(DeleteView):
    model = VolunteerSkill
    template_name = 'dssgmkt/user_profile_skills_skill_remove.html'
    pk_url_kwarg = 'skill_pk'

    def get_success_url(self):
        return reverse('dssgmkt:user_profile_skills_edit', args=[self.kwargs['user_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteer_skill = self.object
        if volunteer_skill and volunteer_skill.user.id == self.request.user.id and self.request.user.id == self.kwargs['user_pk']:
            context['volunteerskill'] = volunteer_skill
            context['breadcrumb'] =  build_breadcrumb([home_link(),
                                                      ("My profile" , reverse('dssgmkt:user_profile', args=[self.kwargs['user_pk']])),
                                                      ("Edit skills", reverse('dssgmkt:user_profile_skills_edit', args=[self.kwargs['user_pk']])),
                                                      ("Remove skill", None)])
            return context
        else:
            raise Http404
