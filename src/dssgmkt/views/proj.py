from datetime import date

from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Case, Q, When
from django.forms import CharField, ModelForm, Textarea
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rules.contrib.views import (
    PermissionRequiredMixin, objectgetter, permission_required,
)

from ..models.common import ReviewStatus
from ..models.proj import (
    Project, ProjectFollower, ProjectLog, ProjectComment, ProjectRole,
    ProjectTask, ProjectTaskRequirement, ProjectStatus, TaskStatus,
    ProjectTaskReview, ProjectTaskRole, VolunteerApplication,
)
from .common import build_breadcrumb, home_link
from dssgmkt.domain.proj import ProjectService


def projects_link(include_link=True):
    return ('Projects', reverse('dssgmkt:proj_list') if include_link else None)

def project_link(project, include_link=True):
    return (project.name, reverse('dssgmkt:proj_info', args=[project.id]) if include_link else None)

def staff_link(project, include_link=True):
    return ('Staff', reverse('dssgmkt:proj_staff', args=[project.id]) if include_link else None)

def volunteers_link(project, include_link=True):
    return ('Volunteers', reverse('dssgmkt:proj_volunteers', args=[project.id]) if include_link else None)

def volunteer_instructions_link(project, include_link=True):
    return ('Volunteer instructions', reverse('dssgmkt:proj_instructions', args=[project.id]) if include_link else None)

def tasks_link(project, include_link=True):
    return ('Tasks', reverse('dssgmkt:proj_task_list', args=[project.id]) if include_link else None)

def edit_task_requirements_link(project, task, include_link=True):
    return ('Edit project task requirements', reverse('dssgmkt:proj_task_requirements_edit', args=[project.id, task.id]) if include_link else None)

def project_breadcrumb(project, *items):
    breadcrumb_items = [home_link(),
                        projects_link(),
                        project_link(project, items)]
    breadcrumb_items += items
    return build_breadcrumb(breadcrumb_items)

class ProjectIndexView(generic.ListView):
    template_name = 'dssgmkt/proj_list.html'
    context_object_name = 'proj_list'
    paginate_by = 1

    def get_queryset(self):
        return Project.objects.order_by('name')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = build_breadcrumb([home_link(),
                                                  projects_link(False)])
        return context


class ProjectView(generic.ListView): ## This is a listview because it is actually showing the list of open tasks
    model = ProjectTask
    template_name = 'dssgmkt/proj_info.html'
    context_object_name = 'project_tasks'

    def get_queryset(self):
        return ProjectTask.objects.filter(accepting_volunteers = True,
                                          project = self.kwargs['proj_pk']).order_by('name')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk = self.kwargs['proj_pk'])
        context['project'] = project
        context['page_tab'] = 'info'
        context['breadcrumb'] = project_breadcrumb(project)
        if not self.request.user.is_anonymous:
            context['user_is_following_project'] = ProjectFollower.objects.filter(project = project, user = self.request.user).exists()
        return context

class ProjectLogView(generic.ListView):
    template_name = 'dssgmkt/proj_log.html'
    context_object_name = 'project_logs'
    paginate_by = 1

    def get_queryset(self):
        project_pk = self.kwargs['proj_pk']
        project = get_object_or_404(Project, pk = project_pk)
        return ProjectLog.objects.filter(project = project).order_by('-change_date')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs['proj_pk']
        project = get_object_or_404(Project, pk = project_pk)
        context['breadcrumb'] = project_breadcrumb(project, ('Change log', None))
        context['project'] = project
        context['page_tab'] = 'log'
        return context

class CreateProjectCommentForm(ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['comment']

class ProjectDiscussionView(generic.ListView):
    template_name = 'dssgmkt/proj_discussion.html'
    context_object_name = 'project_comments'
    paginate_by = 20

    def get_queryset(self):
        project_pk = self.kwargs['proj_pk']
        project = get_object_or_404(Project, pk = project_pk)
        return ProjectComment.objects.filter(project = project).order_by('-comment_date')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs['proj_pk']
        project = get_object_or_404(Project, pk = project_pk)
        context['breadcrumb'] = project_breadcrumb(project, ('Discussion', None))
        context['project'] = project
        context['page_tab'] = 'discussion'
        context['form'] = CreateProjectCommentForm()
        context['user_is_project_member'] = ProjectService.user_is_project_member(self.request.user, project)
        return context

def add_project_comment(request, proj_pk):
    if request.method == 'GET':
        raise Http404
    ## TODO this is a security hole as anybody can post to this view and create new skills
    elif request.method == 'POST': ## TODO move this to the ProjectService in the domain logic layer
        form = CreateProjectCommentForm(request.POST)
        if form.is_valid:
            project_comment = form.save(commit = False)
            project = get_object_or_404(Project, pk = proj_pk)
            project_comment.project = project
            project_comment.author = request.user
            project_comment.save()
            return redirect('dssgmkt:proj_discussion', proj_pk = proj_pk)

class ProjectDeliverablesView(generic.DetailView):
    model = Project
    template_name = 'dssgmkt/proj_deliverables.html'
    pk_url_kwarg = 'proj_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_tab'] = 'deliverables'
        context['breadcrumb'] = project_breadcrumb(context['project'], ('Project deliverables', None))
        context['project'] = self.object
        return context

class ProjectVolunteerInstructionsView(generic.DetailView):
    model = ProjectTask
    template_name = 'dssgmkt/proj_instructions.html'
    pk_url_kwarg = 'proj_pk'

    def get_object(self):
        return ProjectTask.objects.filter(project__pk = self.kwargs['proj_pk'],
                                          projecttaskrole__user = self.request.user,
                                          stage__in=[TaskStatus.STARTED, TaskStatus.WAITING_REVIEW]).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object:
            project_pk = self.kwargs['proj_pk']
            project = get_object_or_404(Project, pk = project_pk)
        else:
            project = self.object.project
        context['page_tab'] = 'instructions'
        context['breadcrumb'] = project_breadcrumb(project, ('Volunteer instructions', None))
        context['project'] = project
        context['project_task'] = self.object
        return context

class CreateProjectTaskReviewForm(ModelForm):
    class Meta:
        model = ProjectTaskReview
        fields = ['volunteer_comment', 'volunteer_effort_hours']

class ProjectTaskReviewCreate(CreateView):
    model = ProjectTaskReview
    fields = ['volunteer_comment', 'volunteer_effort_hours']
    template_name = 'dssgmkt/proj_task_finish.html'

    def get_success_url(self):
        return reverse('dssgmkt:proj_info', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task = get_object_or_404(ProjectTask, pk=self.kwargs['task_pk'])
        context['project'] = project_task.project
        context['project_task'] = project_task
        context['breadcrumb'] = project_breadcrumb(project_task.project,
                                                    volunteer_instructions_link(project_task.project),
                                                    ('Mark work as completed', None))
        context['page_tab']='instructions'
        return context

    def form_valid(self, form):
        project_task_review = form.save(commit=False)
        project_task = get_object_or_404(ProjectTask, pk=self.kwargs['task_pk'])
        project = get_object_or_404(Project, pk=self.kwargs['proj_pk'])
        project_task_review.task = project_task
        project_task_review.review_result = ReviewStatus.NEW
        project_task_review.save()
        project_task.stage = TaskStatus.WAITING_REVIEW
        project_task.save()
        project_task.project.status = ProjectStatus.WAITING_REVIEW
        project_task.project.save()
        return HttpResponseRedirect(self.get_success_url())

class ProjectTaskCancel(DeleteView):
    model = ProjectTaskRole
    template_name = 'dssgmkt/proj_task_cancel.html'

    def get_object(self):
        return get_object_or_404(ProjectTaskRole, task=self.kwargs['task_pk'], user=self.request.user.id)

    def get_success_url(self):
        return reverse('dssgmkt:proj_info', args=[self.object.task.project.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task_role = self.object
        project_task = project_task_role.task
        project = project_task.project
        context['project_task'] = project_task
        context['project'] = project
        context['breadcrumb'] = project_breadcrumb(project,
                                                    volunteer_instructions_link(project_task.project),
                                                    ('Stop volunteering', None))
        context['page_tab']='instructions'
        return context


class ProjectTaskApply(CreateView):
    model = VolunteerApplication
    fields = ['volunteer_application_letter']
    template_name = 'dssgmkt/proj_task_apply.html'

    def get_success_url(self):
        return reverse('dssgmkt:proj_info', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task = get_object_or_404(ProjectTask, pk=self.kwargs['task_pk'])
        project = get_object_or_404(Project, pk=self.kwargs['proj_pk'])
        context['project'] = project
        context['project_task'] = project_task
        context['breadcrumb'] = project_breadcrumb(project, ('Apply to volunteer', None))
        context['page_tab']='info'
        return context

    def form_valid(self, form):
        task_application_request = form.save(commit=False)
        task = get_object_or_404(ProjectTask, pk=self.kwargs['task_pk'])

        task_application_request.status = ReviewStatus.NEW
        task_application_request.task = task
        task_application_request.volunteer = self.request.user
        task_application_request.save()
        return HttpResponseRedirect(self.get_success_url())


class ProjectTaskIndex(generic.ListView):
    model = ProjectTask
    template_name = 'dssgmkt/proj_task_list.html'
    context_object_name = 'project_tasks'

    def get_queryset(self):
        return ProjectTask.objects.filter(project = self.kwargs['proj_pk']).order_by('estimated_start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk = self.kwargs['proj_pk'])
        context['project'] = project
        context['page_tab'] = 'tasklist'
        context['breadcrumb'] = project_breadcrumb(project, tasks_link(project, include_link=False))
        return context



class ProjectTaskEdit(UpdateView):
    model = ProjectTask
    fields = ['name', 'description', 'type', 'onboarding_instructions', 'stage', 'accepting_volunteers', 'estimated_start_date',
                'estimated_end_date', 'estimated_effort_hours', 'task_home_url', 'task_deliverables_url']
    template_name = 'dssgmkt/proj_task_edit.html'
    pk_url_kwarg = 'task_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_task_list', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['proj_pk'])
        context['project'] = project
        context['project_task'] = self.object
        context['breadcrumb'] = project_breadcrumb(project,
                                                    tasks_link(project),
                                                    ('Edit project task', None))
        context['page_tab']='tasklist'
        return context


class ProjectEdit(UpdateView):
    model = Project
    fields = ['name', 'short_summary', 'motivation','solution_description', 'challenges', 'banner_image_url', 'project_cause',
            'project_impact', 'scoping_process', 'available_staff', 'available_data', 'developer_agreement', 'intended_start_date',
            'intended_end_date', 'deliverable_github_url', 'deliverable_management_url', 'deliverable_documentation_url',
            'deliverable_reports_url']
    template_name = 'dssgmkt/proj_info_edit.html'
    pk_url_kwarg = 'proj_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_info', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['proj_pk'])
        context['project'] = project
        context['breadcrumb'] = project_breadcrumb(project, ('Edit project information', None))
        context['page_tab']='info'
        return context


class CreateTaskRequirementForm(ModelForm):
    class Meta:
        model = ProjectTaskRequirement
        fields = ['skill', 'level']

def project_task_requirements_edit_view(request, proj_pk, task_pk):
    if request.method == 'GET':
        task_requirements = ProjectTaskRequirement.objects.filter(task = task_pk)
        task = get_object_or_404(ProjectTask, pk = task_pk)
        project = get_object_or_404(Project, pk = proj_pk)
        return render(request, 'dssgmkt/proj_task_requirements_edit.html',
                            {
                            'project': project,
                            'page_tab': 'tasklist',
                            'project_task': task,
                            'task_requirements': task_requirements,
                            'breadcrumb': project_breadcrumb(project,
                                                                tasks_link(project),
                                                                edit_task_requirements_link(project, task, include_link=False)),
                            'add_requirement_form': CreateTaskRequirementForm()
                            })
    ## TODO this is a security hole as anybody can post to this view and create new skills
    elif request.method == 'POST':
        form = CreateTaskRequirementForm(request.POST)
        if form.is_valid:
            requirement = form.save(commit = False)
            project_task = get_object_or_404(ProjectTask, pk = task_pk)
            requirement.task = project_task
            requirement.save()
            return redirect('dssgmkt:proj_task_requirements_edit', proj_pk = proj_pk, task_pk = task_pk)

class ProjectTaskRequirementEdit(UpdateView):
    model = ProjectTaskRequirement
    fields = ['level']
    template_name = 'dssgmkt/proj_task_requirements_requirement_edit.html'
    pk_url_kwarg = 'requirement_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_task_requirements_edit', args=[self.kwargs['proj_pk'],self.kwargs['task_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_requirement = self.object
        if task_requirement:
            project_task = task_requirement.task
            project = project_task.project
            context['project'] = project
            context['project_task'] = project_task
            context['task_requirement'] = task_requirement
            context['page_tab'] = 'tasklist'
            context['breadcrumb'] =  project_breadcrumb(project,
                                                            tasks_link(project),
                                                            edit_task_requirements_link(project, project_task),
                                                            ('Edit requirement', None))
            return context
        else:
            raise Http404

class ProjectTaskRequirementRemove(DeleteView):
    model = ProjectTaskRequirement
    template_name = 'dssgmkt/proj_task_requirements_requirement_remove.html'
    pk_url_kwarg = 'requirement_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_task_requirements_edit', args=[self.kwargs['proj_pk'],self.kwargs['task_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_requirement = self.object
        if task_requirement:
            project_task = task_requirement.task
            project = project_task.project
            context['project'] = project
            context['project_task'] = project_task
            context['task_requirement'] = task_requirement
            context['page_tab'] = 'tasklist'
            context['breadcrumb'] =  project_breadcrumb(project,
                                                            tasks_link(project),
                                                            edit_task_requirements_link(project, project_task),
                                                            ('Remove requirement', None))
            return context
        else:
            raise Http404

class ProjectTaskRemove(DeleteView):
    model = ProjectTask
    template_name = 'dssgmkt/proj_task_remove.html'
    pk_url_kwarg = 'task_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_task_list', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task = self.object
        if project_task:
            project = project_task.project
            context['project'] = project
            context['project_task'] = project_task
            context['page_tab'] = 'tasklist'
            context['breadcrumb'] =  project_breadcrumb(project,
                                                            tasks_link(project),
                                                            ('Delete task', None))
            return context
        else:
            raise Http404


def create_default_project_task(request, proj_pk):
    if request.method == 'GET':
        raise Http404
    ## TODO this is a security hole as anybody can post to this view and create new skills
    elif request.method == 'POST': ## TODO move this to the ProjectTaskService in the domain logic layer
        project_task = ProjectTask()
        project_task.name = 'New project task'
        project_task.description = 'This is the task description'
        project_task.onboarding_instructions = 'These are the volunteer onboarding instructions'
        project_task.stage = TaskStatus.NOT_STARTED
        project_task.accepting_volunteers = False
        project_task.project = get_object_or_404(Project, pk = proj_pk)
        project_task.percentage_complete = 0
        project_task.business_area = 'no'
        project_task.estimated_start_date = date.today()
        project_task.estimated_end_date = date.today()
        project_task.save()
        return redirect('dssgmkt:proj_task_list', proj_pk = proj_pk)


class CreateProjectRoleForm(ModelForm):
    class Meta:
        model = ProjectRole
        fields = ['role', 'user']

def project_staff_view(request, proj_pk):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk = proj_pk)
        staff_page_size = 50
        project_staff = project.projectrole_set.all().order_by('role')
        staff_paginator = Paginator(project_staff, staff_page_size)
        staff_page = staff_paginator.get_page(request.GET.get('staff_page', 1))

        return render(request, 'dssgmkt/proj_staff.html',
                            {'project': project,
                            'page_tab': 'staff',
                            'breadcrumb': project_breadcrumb(project, ('Staff', None)),

                            'project_staff': staff_page,

                            'add_staff_form': CreateProjectRoleForm(),

                            'user_is_project_owner': True, ## TODO remove this
                            })
    ## TODO this is a security hole as staff can post to this view and create new members
    elif request.method == 'POST':
        form = CreateProjectRoleForm(request.POST)
        if form.is_valid:
            project_role = form.save(commit = False)
            project = get_object_or_404(Project, pk = proj_pk)
            project_role.project = project
            project_role.save()
            return redirect('dssgmkt:proj_staff', proj_pk = proj_pk)



def project_volunteers_view(request, proj_pk):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk = proj_pk)

        volunteers_page_size = 1
        volunteers = ProjectTaskRole.objects.filter(task__project__id = proj_pk)
        volunteers_paginator = Paginator(volunteers, volunteers_page_size)
        volunteers_page = volunteers_paginator.get_page(request.GET.get('volunteers_page', 1))

        applications_page_size = 50
        volunteer_applications = VolunteerApplication.objects.filter(task__project__id = proj_pk).order_by(
                Case(When(status=ReviewStatus.NEW, then=0),
                     When(status=ReviewStatus.ACCEPTED, then=1),
                     When(status=ReviewStatus.REJECTED, then=2)), '-application_date')
        volunteer_applications_paginator = Paginator(volunteer_applications, applications_page_size)
        applications_page = volunteer_applications_paginator.get_page(request.GET.get('applications_page', 1))

        return render(request, 'dssgmkt/proj_volunteers.html',
                            {'project': project,
                            'page_tab': 'volunteers',
                            'breadcrumb': project_breadcrumb(project, ('Volunteers', None)),

                            'volunteers': volunteers_page,
                            'volunteer_applications': applications_page,

                            'user_is_project_owner': True, ## TODO remove this
                            })


class ProjectRoleEdit(SuccessMessageMixin, UpdateView):
    model = ProjectRole
    fields = ['role']
    template_name = 'dssgmkt/proj_staff_edit.html'
    pk_url_kwarg = 'role_pk'
    success_message = 'Role edited successfully'

    def get_success_url(self):
        return reverse('dssgmkt:proj_staff', args=[self.object.project.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_role = self.object
        if project_role and project_role.project.id == self.kwargs['proj_pk']:
            project = self.object.project
            context['project'] = project
            context['breadcrumb'] =  project_breadcrumb(project,
                                                        staff_link(project),
                                                        ('Edit staff member', None))
            context['page_tab'] = 'staff'
            return context
        else:
            raise Http404

class ProjectRoleRemove(DeleteView):
    model = ProjectRole
    template_name = 'dssgmkt/proj_staff_remove.html'
    pk_url_kwarg = 'role_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_staff', args=[self.object.project.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_role = self.object
        if project_role and project_role.project.id == self.kwargs['proj_pk']:
            project = self.object.project
            context['project'] = project
            context['breadcrumb'] =  project_breadcrumb(project,
                                                        staff_link(project),
                                                        ('Remove staff member', None))
            context['page_tab']='staff'
            return context
        else:
            raise Http404

class EditProjectTaskRoleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProjectTaskRoleForm, self).__init__(*args, **kwargs)
        print(self.instance)
        self.fields['task'].queryset = ProjectTask.objects.filter(project=self.instance.task.project)

    class Meta:
        model = ProjectTaskRole
        fields = ['task']

class ProjectTaskRoleEdit(SuccessMessageMixin, UpdateView):
    model = ProjectTaskRole
    form_class = EditProjectTaskRoleForm
    template_name = 'dssgmkt/proj_task_volunteer_edit.html'
    pk_url_kwarg = 'task_role_pk'
    success_message = 'Volunteer edited successfully'

    def get_success_url(self):
        return reverse('dssgmkt:proj_volunteers', args=[self.object.task.project.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task_role = self.object
        if project_task_role and project_task_role.task.id == self.kwargs['task_pk'] and project_task_role.task.project.id == self.kwargs['proj_pk']:
            project_task = project_task_role.task
            project = project_task.project
            context['project'] = project
            context['breadcrumb'] =  project_breadcrumb(project,
                                                        volunteers_link(project),
                                                        ('Change volunteer task', None))
            context['page_tab'] = 'volunteers'
            return context
        else:
            raise Http404

class ProjectTaskRoleRemove(DeleteView):
    model = ProjectTaskRole
    template_name = 'dssgmkt/proj_volunteer_remove.html'

    def get_object(self):
        return get_object_or_404(ProjectTaskRole, pk = self.kwargs['task_role_pk'])

    def get_success_url(self):
        return reverse('dssgmkt:proj_volunteers', args=[self.object.task.project.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_task_role = self.object
        project_task = project_task_role.task
        project = project_task.project
        context['project_task'] = project_task
        context['project'] = project
        context['breadcrumb'] = project_breadcrumb(project,
                                                    volunteers_link(project),
                                                    ('Remove volunteer', None))
        context['page_tab']='volunteers'
        return context

class ProjectVolunteerApplicationEdit(UpdateView):
    model = VolunteerApplication
    fields = ['status', 'public_reviewer_comments', 'private_reviewer_notes']
    template_name = 'dssgmkt/proj_volunteer_application_review.html'
    pk_url_kwarg = 'volunteer_application_pk'

    def get_success_url(self):
        return reverse('dssgmkt:proj_volunteers', args=[self.kwargs['proj_pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['proj_pk'])
        volunteer_application = self.object
        if volunteer_application and volunteer_application.task.id == self.kwargs['task_pk'] and volunteer_application.task.project.id == self.kwargs['proj_pk']:
            context['project'] = project
            context['breadcrumb'] = project_breadcrumb(project,
                                                        volunteers_link(project),
                                                        ('Review volunteer', None))
            context['page_tab']='volunteers'
            return context
        else:
            raise Http404

def follow_project_view(request, proj_pk):
    if request.method == 'GET':
        raise Http404
    ## TODO this is a security hole as anybody can post to this view and create new skills
    elif request.method == 'POST':
        project = get_object_or_404(Project, pk = proj_pk)
        project_follower = ProjectFollower.objects.filter(project = project, user = request.user).first()
        if project_follower:
            project_follower.delete()
        else:
            project_follower = ProjectFollower()
            project_follower.project = project
            project_follower.user = request.user
            project_follower.save()
        return redirect('dssgmkt:proj_info', proj_pk = proj_pk)
