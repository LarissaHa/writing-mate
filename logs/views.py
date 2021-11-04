import re
from django.db.models.fields import DateTimeField
from django.views.generic import CreateView
from django.db.models.functions.datetime import TruncWeek
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.text import slugify
from .models import Log, Project, Profile
from .forms import LogForm, ProfileEditForm, ProjectForm, WordcountForm, LogEditForm
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, BoxSelectTool, Span
from bokeh.palettes import Spectral6, magma
from bokeh.models import LinearColorMapper
from bokeh.transform import factor_cmap
from django.db.models import Sum, Count, Min
from django.db.models.functions import Extract
import dateparser
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db.models.functions import TruncMonth, TruncYear, TruncWeek, TruncDay
from .utils import time_between


def xdsoft_datetimepicker(request, project_slug=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if request.method == "POST":
        form = LogForm(request, request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('/logs/')
    else:
        if project_slug is not None:
            project = get_object_or_404(Project, slug=project_slug)
            form = LogForm(request, initial={'project': project})
        else:
            form = LogForm(request)
    return render(request, 'logs/xdsoft_event_form.html', {'form': form})


def deal_with_projects(temp, user):
    projects = [{
        "title": p.title,
        "status": p.status,
        "unit": p.unit,
        "count": Log.objects.filter(project=p, user=user).aggregate(Sum('count'))["count__sum"],
        "goal": p.goal,
        "slug": p.slug,
        "synopsis": p.synopsis,
        "subtitle": p.subtitle,
        "progress": "0%",
        "color": p.color,
        "priority": p.priority,
        "image": p.image
    } for p in temp]
    for p in projects:
        if p["count"] is None:
            continue
        else:
            p["progress"] = str(round((p["count"] / p["goal"] * 100), 2)) + "%"
        if p["color"] == "":
            p["color"] = "#6f42c1"
    return projects


def get_profile_image(user):
    profile = Profile.objects.filter(user=user)
    try:
        image = profile[0].profile_image.url
    except:
        image = ""
    return image


def chart(data, goal=None):
    #print(data[0])
    x = [(str(d["level"]), "") for d in data]
    levels = [str(d["level"]) for d in data]
    counts = tuple([d["total_count"] for d in data])

    plot = figure(
        x_range=FactorRange(*x),
        plot_height=250,
        title="your progress",
        toolbar_location="below",
        tools="pan,wheel_zoom,box_zoom,reset"
    )
    plot.add_tools(BoxSelectTool(dimensions="width"))
    # plot.add_tools(WheelZoomTool())
    source = ColumnDataSource(data=dict(x=x, counts=counts, levels=levels))
    if goal:
        hline = Span(location=goal, dimension='width', line_color='gray', line_width=3)
        plot.renderers.extend([hline])
    plot.vbar(
        x='x',
        top='counts',
        width=0.9,
        source=source,
        line_color="white",
        fill_color=factor_cmap('levels', palette=magma(len(levels)), factors=list(set(levels)))
    )

    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None
    plot.sizing_mode='stretch_both'

    script, div = components(plot)
    return script, div


def community(request):
    profile_pic = get_profile_image(request.user)
    profiles = Profile.objects.filter(is_public=True)
    projects = Project.objects.filter(is_public=True)
    logs = Log.objects.filter(is_public=True)
    return render(request, 'logs/community.html', {'profiles': profiles, 'logs': logs, 'projects': projects, 'profile_pic': profile_pic})


def not_allowed(request):
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/not_allowed.html', {'profile_pic': profile_pic})


def contact(request):
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/contact.html', {'profile_pic': profile_pic})


def release_notes(request):
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/release_notes.html', {'profile_pic': profile_pic})


def imprint(request):
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/imprint.html', {'profile_pic': profile_pic})


def register(request):
    profile_pic = get_profile_image(request.user)
    return render(request, 'registration/register.html', {'profile_pic': profile_pic})


def welcome(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    else:
        profile_pic = get_profile_image(request.user)
        try:
            project = Project.objects.filter(user=request.user).latest('created_at')
        except:
            project = None
        try:
            log = Log.objects.filter(user=request.user, is_update=False).latest('date', 'time')
        except:
            log = None
        try:
            temp = Project.objects.filter(user=request.user).order_by("priority", "-created_at")
            projects = deal_with_projects(temp, request.user)
        except:
            projects = None
        script, div, metrics, progress = home_stats(request)
        return render(request, 'logs/home.html', {
            'project': project, 
            'log': log, 
            'script': script, 
            'div': div, 
            'metrics': metrics, 
            'projects': projects, 
            'profile_pic': profile_pic,
            'progress': progress
        })


def wordcount_form(request, slug):
    project = get_object_or_404(Project, slug=slug)
    total_count = Log.objects.filter(project=project, user=request.user).aggregate(Sum('count'))["count__sum"]
    if total_count is None:
        total_count = 0
    if request.method == "POST":
        form = WordcountForm(request, request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.project = project
            log.date = date.today()
            log.time = datetime.now()
            count = log.count
            log.count = count - total_count
            log.is_update = True
            log.save()
            return None
    else:
        form = WordcountForm(request, initial={'count': total_count})
    return form


def wordcount(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    profile_pic = get_profile_image(request.user)
    form = wordcount_form(request, slug)
    return render(request, 'logs/wordcount.html', {'wc_form': form, 'profile_pic': profile_pic})


def logs_new(request, project_slug=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if request.method == "POST":
        form = LogForm(request, request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            if project_slug:
                return redirect(f'/projects/{project_slug}')
            else:
                return redirect('/logs/')
    else:
        if project_slug is not None:
            project = get_object_or_404(Project, slug=project_slug)
            form = LogForm(request, initial={'project': project, 'date': date.today(), 'time': timezone.localtime(timezone.now())})
        else:
            form = LogForm(request, initial={'date': date.today(), 'time': timezone.localtime(timezone.now())})
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/logs_new.html', {'form': form, 'profile_pic': profile_pic})


def logs_edit(request, pk):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    log = get_object_or_404(Log, pk=pk)
    if log.user != request.user:
        return redirect('/not_allowed/')
    if request.method == "POST":
        form = LogEditForm(request.POST, instance=log)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('/logs/')
    else:
        form = LogEditForm(instance=log)
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/logs_edit.html', {'form': form, "log_pk": pk, 'profile_pic': profile_pic})


def logs_delete(request, pk):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    to_delete = get_object_or_404(Log, pk=pk)
    if to_delete.user != request.user:
        return redirect(request, 'logs/not_allowed.html')
    to_delete.delete()
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/deleted_successfully.html', {'profile_pic': profile_pic})


def logs2(request):
    print(request.user)
    logs = Log.objects.filter(user=request.user).order_by("date")
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/logs.html', {'logs': logs, 'profile_pic': profile_pic})


def projects(request, key=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if key == "newest":
        temp = Project.objects.filter(user=request.user).order_by("-created_at")
    elif key == "oldest":
        temp = Project.objects.filter(user=request.user).order_by("created_at")
    else:
        temp = Project.objects.filter(user=request.user).order_by("priority", "-created_at")
    projects = deal_with_projects(temp, request.user)
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/projects.html', {'projects': projects, 'profile_pic': profile_pic})


def calc_goals(user, project):
    if project.deadline is not None and project.deadline > date.today():
        x = 1
        count_today = Log.objects.filter(project=project, user=user, date__lt=date.today()).aggregate(Sum('count'))["count__sum"]
        count_update = Log.objects.filter(project=project, user=user, is_update=True).aggregate(Sum('count'))["count__sum"]
        count = (
            (0 if count_today is None else count_today)
            + (0 if count_update is None else count_update)
        )
        logs_today = Log.objects.filter(project=project, user=user, date=timezone.localtime(timezone.now()), is_update=False)
        if len(logs_today) <= 0:
            x = x - 1
        todo = project.goal - count
        difference = project.deadline - timezone.localtime(timezone.now()).date()
        daily_goal = round(todo / difference.days)
        if ((difference.days+x) / 7) >=1:
            weekly_goal = round(todo / (difference.days / 7))
        else:
            weekly_goal = None
        return {"daily_goal": daily_goal, "weekly_goal": weekly_goal}
    return None


def project_view(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    project = get_object_or_404(Project, slug=slug)
    target = 'logs/project_view.html'
    if project.user != request.user:
        if project.is_public is False:
            return redirect('/not_allowed/')
        else:
            target = 'logs/project_view_others.html'
    count = Log.objects.filter(project=project).aggregate(Sum('count'))["count__sum"]
    logs = Log.objects.filter(project=project, is_update=False).order_by("-date", "-time")
    n_logs = len(logs)
    logs = logs[:5]
    if count is None:
        progress = "0%"
    else:
        progress = str(round((count / project.goal * 100), 2)) + "%"
    goals = calc_goals(request.user, project)
    count_today = Log.objects.filter(project=project, date=timezone.localtime(timezone.now()), is_update=False).aggregate(Sum('count'))["count__sum"]
    if count_today is None or goals is None:
        progress_today = "0%"
    else:
        progress_today = str(round((count_today / goals["daily_goal"] * 100), 2)) + "%"
        #if goals["weekly_goal"] is None:
        #    progress_thisweek = "0%"
        #else:
        #    count_thisweek = Log.objects.filter(project=project, user=request.user, date=date.today()).aggregate(Sum('count'))["count__sum"]
        #    progress_thisweek = str(round((count_thisweek / goals["weekly_goal"] * 100), 2)) + "%"
    wc_form = wordcount_form(request, slug)
    if wc_form is None:
        return redirect('project_view', slug=project.slug)
    color = project.color
    if project.color == None:
        project.color = "#6f42c1"
    profile_pic = get_profile_image(request.user)
    return render(request, target, {
        'project': project,
        'color': color,
        'count': count,
        'logs': logs,
        'progress': progress,
        'n_logs': n_logs,
        'goals': goals,
        'count_today': count_today,
        'progress_today': progress_today,
        'wc_form': wc_form, 
        'profile_pic': profile_pic
    })


def project_new(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.slug = slugify(str(project.user) + " " + str(project.title))
            project.created_at = timezone.localtime(timezone.now())
            project.save()
            return redirect('project_view', slug=project.slug)
    else:
        form = ProjectForm()
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/project_new.html', {'form': form, 'profile_pic': profile_pic})


def project_edit(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    project = get_object_or_404(Project, slug=slug)
    if project.user != request.user:
        return redirect('/not_allowed/')
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('project_view', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/project_edit.html', {'form': form, "project_slug": slug, 'profile_pic': profile_pic})


def project_delete(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    to_delete = get_object_or_404(Project, slug=slug)
    if to_delete.user != request.user:
        return redirect(request, 'logs/not_allowed.html')
    to_delete.delete()
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/deleted_successfully.html', {'profile_pic': profile_pic})


def home_stats(request):
    stats = []
    start_datime = timezone.localtime(timezone.now()) - timedelta(days=6)
    for day in time_between(start_datime, timezone.localtime(timezone.now()), "daily"):
        stats.append({"level": day.strftime("%A"), "total_count": 0})
    temp = Log.objects.filter(user=request.user, is_update=False, date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncDay('date')).values('level').annotate(total_count=Sum('count'))
    for s in stats:
        for t in temp:
            if s["level"] == t["level"].strftime("%A"):
                s["total_count"] = t["total_count"]
    logs = Log.objects.filter(user=request.user, is_update=False).extra(select={'level': 'date(date)'}).values('level')
    written_on_days = len(logs.distinct())
    total_count = sum([l["total_count"] for l in logs.annotate(total_count=Sum('count'))])
    total_logs = logs.count()
    metrics = {"written_on_days": written_on_days, "total_count": total_count, "total_logs": total_logs}

    count_today = Log.objects.filter(user=request.user, date=date.today()).aggregate(Sum('count'))["count__sum"]
    profile = Profile.objects.filter(user=request.user)
    personal_goal = None
    goal_unit = None
    if len(profile) > 0:
        personal_goal = profile[0].daily_goal
        goal_unit = profile[0].goal_unit
    if count_today is None or personal_goal is None:
        progress_today = "0%"
    else:
        progress_today = str(round((count_today / personal_goal * 100), 2)) + "%"
    progress = {"personal_goal": personal_goal, "count_today": count_today, "progress_today": progress_today, "goal_unit": goal_unit}

    script, div = chart(stats, personal_goal)
    return script, div, metrics, progress


def stats(request, mode="days"):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    stats = []
    if mode == "weeks":
        level = "Week"
        # last 15 weeks
        start_datime = timezone.localtime(timezone.now()) - timedelta(weeks=15)
        for week in time_between(start_datime, timezone.localtime(timezone.now()), "weekly"):
            stats.append({"level": week.strftime('%V'), "total_count": 0})
        temp = Log.objects.filter(user=request.user, is_update=False, date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncWeek('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime('%V'):
                    s["total_count"] = t["total_count"]
    elif mode == "months":
        level = "Month"
        # last 12 months
        start_datime = timezone.localtime(timezone.now()) - timedelta(weeks=51)
        for month in time_between(start_datime, timezone.localtime(timezone.now()), "monthly"):
            stats.append({"level": month.strftime("%b"), "total_count": 0})
        temp = Log.objects.filter(user=request.user, is_update=False, date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncMonth('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime('%b'):
                    s["total_count"] = t["total_count"]
    elif mode == "years":
        level = "Year"
        # everything
        start_datime = timezone.localtime(timezone.now()) - timedelta(weeks=200) # greatest day in DB
        for year in time_between(start_datime, timezone.localtime(timezone.now()), "yearly"):
            stats.append({"level": year.year, "total_count": 0})
        stats.append({"level": timezone.localtime(timezone.now()).year, "total_count": 0})
        temp = Log.objects.filter(user=request.user, is_update=False).annotate(level=TruncYear('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].year:
                    s["total_count"] = t["total_count"]
        stats = [i for n, i in enumerate(stats) if i not in stats[n + 1:]]
    else:
        level = "Day"
        # last 30 days
        start_datime = timezone.localtime(timezone.now()) - timedelta(days=30)
        for day in time_between(start_datime, timezone.localtime(timezone.now()), "daily"):
            stats.append({"level": day.strftime("%d"), "total_count": 0})
        temp = Log.objects.filter(user=request.user, is_update=False, date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncDay('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime("%d"):
                    s["total_count"] = t["total_count"]
    start_datime
    logs = Log.objects.filter(user=request.user, is_update=False, date__gt=start_datime).extra(select={'level': 'date(date)'}).values('level')
    written_on_days = len(logs.distinct())
    total_count = sum([l["total_count"] for l in logs.annotate(total_count=Sum('count'))])
    total_logs = logs.count()
    metrics = {"written_on_days": written_on_days, "total_count": total_count, "total_logs": total_logs}
    script, div = chart(stats)
    profile_pic = get_profile_image(request.user)
    return render(
        request,
        'logs/stats.html',
        {'script': script, 'div': div, 'stats': stats, 'level': level, 'metrics': metrics, 'profile_pic': profile_pic}
    )


def logs(request, slug=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    projects = Project.objects.filter(user=request.user).order_by("-created_at")
    profile_pic = get_profile_image(request.user)
    if "GET" == request.method:
        if slug is None:
            logs = Log.objects.filter(user=request.user, is_update=False).order_by("-date", "-time")[:20]
            filtered_by = "filter by project"
            return render(request, 'logs/logs.html', {'logs': logs, 'projects': projects, 'filtered_by': filtered_by, 'profile_pic': profile_pic})
        else:
            project = get_object_or_404(Project, slug=slug, user=request.user)
            filtered_by = project.title
            logs = Log.objects.filter(project=project, user=request.user, is_update=False).order_by("-date", "-time")[:20]
            return render(request, 'logs/logs.html', {'logs': logs, 'projects': projects, 'filtered_by': filtered_by, 'profile_pic': profile_pic})
            # return render(request, "logs/logs.html", data)
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            # messages.error(request,'File is not CSV type')
            return redirect("/logs/")
        # if file is too large, return
        if csv_file.multiple_chunks():
            # messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return redirect("/logs/")

        file_data = csv_file.read().decode("utf-8")

        # project = request.content("project")
        project = request.POST.get('project')
        new_project = Project()
        new_project.title = project
        new_project.user = request.user
        new_project.save()

        lines = file_data.split("\n")
        # loop over the lines and save them in db. If error , store as string and then display
        i = 0
        for line in lines:
            if i == 0:
                i = i + 1
                pass
            else:
                fields = line.split(",")
                new = Log()
                new.project = new_project
                new.date = dateparser.parse(fields[0]).strftime('%Y-%m-%d')
                new.time = dateparser.parse(fields[1]).strftime('%H:%M')
                new.count = fields[2]
                new.note = fields[6]
                new.user = request.user
                new.save()
                i = i + 1
            #data_dict = {}
            #data_dict["project"] = new_project
            #data_dict["date"] = fields[0]
            #data_dict["time"] = fields[1]
            #data_dict["count"] = fields[2]
            #data_dict["note"] = fields[6]
            #print(data_dict)
            #try:
            #    form = LogForm(data_dict)
            #    if form.is_valid():
            #        form.save()
            #    else:
            #        print(data_dict)
                    # print(form)
           #         print("blubb")
                    # logging.getLogger("error_logger").error(form.errors.as_json())
          #          pass
                    
            #except Exception as e:
            #    print(e)
            #    pass

    except Exception as e:
        print("3")
        print(e)
        # logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        # messages.error(request,"Unable to upload file. "+repr(e))
        pass

    return redirect("/logs/")


def profile(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    else:
        return redirect(f'/profile/{request.user.username}/')


def profile_view(request, user=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if user is None:
        user_name = request.user.username
    else:
        user_name = user
    if request.user.username != user_name:
        looking_for = get_object_or_404(User, username=user_name)
        temp = Project.objects.filter(is_public=True, user=looking_for).order_by("priority", "-created_at")
        profile = get_object_or_404(Profile, user=looking_for, is_public=True)
    else:
        profile, created = Profile.objects.get_or_create(user=request.user)
        if created is True:
            return redirect(f'/profile/{user_name}/')
        temp = Project.objects.filter(user=request.user).order_by("priority", "-created_at")
    projects = deal_with_projects(temp, request.user)
    profile_pic = get_profile_image(request.user)
    profile_color = profile.color
    if profile_color == "" or profile_color is None:
        profile_color = "#6f42c1"
    return render(request, 'logs/profile_view.html', {
        'profile': profile,
        'profile_color': profile_color,
        'user_name': user_name,
        'projects': projects,
        'profile_pic': profile_pic
    })


def profile_settings(request, user=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if user is None:
        user_name = request.user.username
    else:
        user_name = user
    if request.user.username != user_name:
        return redirect('/not_allowed/')
    else:
        profile = get_object_or_404(Profile, user=request.user)
        if request.method == "POST":
            form = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('profile_view', user=user_name)
        else:
            form = ProfileEditForm(instance=profile)
    profile_pic = get_profile_image(request.user)
    return render(request, 'logs/profile_settings.html', {'form': form, 'profile_pic': profile_pic})


from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes



def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "WRITING MATE - Password Reset Requested"
					email_template_name = "password_reset_email.txt"
					c = {
					"email": user.email,
					'domain': '127.0.0.1:8000',
					'site_name': 'writing mate',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'larissa@gasleuchte.de' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password-reset.html", context={"password_reset_form": password_reset_form})