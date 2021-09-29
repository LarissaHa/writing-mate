import re
from django.db.models.fields import DateTimeField
from django.db.models.functions.datetime import TruncWeek
from django.shortcuts import get_object_or_404, render, redirect
from .models import Log, Project, Profile
from .forms import LogForm, ProjectForm
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, BoxSelectTool
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
from django.db.models import Sum, Count, Min
from django.db.models.functions import Extract
import dateparser
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth, TruncYear, TruncWeek
from .utils import time_between


def chart(data):
    #print(data[0])
    x = [(str(d["level"]), "") for d in data]
    levels = [str(d["level"]) for d in data]
    counts = tuple([d["total_count"] for d in data])

    years = ['2015', '2016', '2017']

    source = ColumnDataSource(data=dict(x=x, counts=counts))
    plot = figure(
        x_range=FactorRange(*x),
        plot_height=250,
        title="your progress",
        toolbar_location="below",
        tools="pan,wheel_zoom,box_zoom,reset"
    )
    plot.add_tools(BoxSelectTool(dimensions="width"))
    # plot.add_tools(WheelZoomTool())
    plot.vbar(
        x='x',
        top='counts',
        width=0.9,
        source=source,
        line_color="white",
        fill_color=factor_cmap(
            'x',
            palette=Spectral6,
            factors=levels,
            start=1,
            end=2
        )
    )

    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None
    plot.sizing_mode='stretch_both'

    script, div = components(plot)
    return script, div


def welcome(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    else:
        project = Project.objects.filter(user=request.user).latest('created_at')
        log = Log.objects.filter(user=request.user).latest('date')
        return render(request, 'logs/home.html', {'project': project, 'log': log})


def profile(request):
    user = Profile.objects.all()
    print(user)
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'logs/profile.html', {'profile': profile})


def logs_new(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if request.method == "POST":
        form = LogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('/logs/') #, {'profile': profile})
    else:
        form = LogForm()
    return render(request, 'logs/logs_new.html', {'form': form})


def logs_edit(request, pk):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    log = get_object_or_404(Log, pk=pk)
    if request.method == "POST":
        form = LogForm(request.POST, instance=log)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('/logs/') #, {'profile': profile})
    else:
        form = LogForm(instance=log)
    return render(request, 'logs/logs_edit.html', {'form': form})


def logs2(request):
    print(request.user)
    logs = Log.objects.filter(user=request.user).order_by("date")
    return render(request, 'logs/logs.html', {'logs': logs})


def projects(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    temp = Project.objects.filter(user=request.user).order_by("-created_at")
    projects = [{
        "title": p.title,
        "status": p.status,
        "unit": p.unit,
        "count": Log.objects.filter(project=p, user=request.user).aggregate(Sum('count'))["count__sum"],
        "goal": p.goal,
        "slug": p.slug,
        "progress": "0%"
    } for p in temp]
    for p in projects:
        if p["count"] is None:
            continue
        else:
            p["progress"] = str(p["count"] / p["goal"] * 100) + "%"
    return render(request, 'logs/projects.html', {'projects': projects})


def project_view(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    project = get_object_or_404(Project, slug=slug, user=request.user)
    count = Log.objects.filter(project=project, user=request.user).aggregate(Sum('count'))["count__sum"]
    logs = Log.objects.filter(project=project, user=request.user).order_by("-date")
    n_logs = len(logs)
    logs = logs[:5]
    if count is None:
        progress = "0%"
    else:
        progress = str(count / project.goal * 100) + "%"
    return render(request, 'logs/project_view.html', {'project': project, 'count': count, 'logs': logs, 'progress': progress, 'n_logs': n_logs})


def project_new(request):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('project_view', slug=project.slug)  #, {'profile': profile})
    else:
        form = ProjectForm()
    return render(request, 'logs/project_new.html', {'form': form})


def project_edit(request, slug):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    project = get_object_or_404(Project, slug=slug)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('project_view', slug=project.slug)  #, {'profile': profile})
    else:
        form = ProjectForm(instance=project)
    return render(request, 'logs/project_edit.html', {'form': form})


def stats(request, mode="days"):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    stats = []
    if mode == "weeks":
        level = "Week"
        # last 15 weeks
        start_datime = datetime.now() - timedelta(weeks=15)
        for week in time_between(start_datime, datetime.now(), "weekly"):
            stats.append({"level": week.strftime('%V'), "total_count": 0})
        temp = Log.objects.filter(user=request.user).filter(date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncWeek('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime('%V'):
                    s["total_count"] = t["total_count"]
    elif mode == "months":
        level = "Month"
        # last 12 months
        start_datime = datetime.now() - timedelta(weeks=53)
        for month in time_between(start_datime, datetime.now(), "monthly"):
            stats.append({"level": month.strftime("%b %Y"), "total_count": 0})
        temp = Log.objects.filter(user=request.user).filter(date__gt=start_datime).extra(select={'day': 'date(date)'}).annotate(level=TruncMonth('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime('%b %Y'):
                    s["total_count"] = t["total_count"]
    elif mode == "years":
        level = "Year"
        # everything
        start_datime = datetime.now() - timedelta(weeks=200) # greatest day in DB
        for year in time_between(start_datime, datetime.now(), "yearly"):
            stats.append({"level": year.year, "total_count": 0})
        stats.append({"level": datetime.now().year, "total_count": 0})
        temp = Log.objects.filter(user=request.user).annotate(level=TruncYear('date')).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].year:
                    s["total_count"] = t["total_count"]
    else:
        level = "Day"
        # last 30 days
        start_datime = datetime.now() - timedelta(days=30)
        for day in time_between(start_datime, datetime.now(), "daily"):
            stats.append({"level": day.strftime("%d %b"), "total_count": 0})
        temp = Log.objects.filter(user=request.user).filter(date__gt=start_datime).extra(select={'level': 'date(date)'}).values('level').annotate(total_count=Sum('count'))
        for s in stats:
            for t in temp:
                if s["level"] == t["level"].strftime("%d %b"):
                    s["total_count"] = t["total_count"]
    start_datime
    logs = Log.objects.filter(user=request.user).filter(date__gt=start_datime).extra(select={'level': 'date(date)'}).values('level')
    written_on_days = len(logs.distinct())
    total_count = sum([l["total_count"] for l in logs.annotate(total_count=Sum('count'))])
    total_logs = logs.count()
    metrics = {"written_on_days": written_on_days, "total_count": total_count, "total_logs": total_logs}
    script, div = chart(stats)
    return render(
        request,
        'logs/stats.html',
        {'script': script, 'div': div, 'stats': stats, 'level': level, 'metrics': metrics}
    )


def logs(request, slug=None):
    if request.user.is_anonymous:
        return render(request, 'logs/home.html')
    projects = Project.objects.filter(user=request.user).order_by("-created_at")
    if "GET" == request.method:
        if slug is None:
            logs = Log.objects.filter(user=request.user).order_by("-date")[:20]
            filtered_by = "filter by project"
            return render(request, 'logs/logs.html', {'logs': logs, 'projects': projects, 'filtered_by': filtered_by})
        else:
            project = get_object_or_404(Project, slug=slug, user=request.user)
            filtered_by = project.title
            logs = Log.objects.filter(project=project, user=request.user).order_by("-date")[:20]
            return render(request, 'logs/logs.html', {'logs': logs, 'projects': projects, 'filtered_by': filtered_by})
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
