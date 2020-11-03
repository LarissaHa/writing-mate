import re
from django.shortcuts import get_object_or_404, render, redirect
from .models import Log, Project, Profile
from .forms import LogForm
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, BoxSelectTool
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
from django.db.models import Sum, Count
from django.db.models.functions import Extract
import dateparser


def chart(data):
    print(data[0])
    x = [(str(d["level"]), "") for d in data]
    levels = [str(d["level"]) for d in data]
    counts = tuple([d["total_count"] for d in data])

    years = ['2015', '2016', '2017']

    source = ColumnDataSource(data=dict(x=x, counts=counts))
    plot = figure(
        x_range=FactorRange(*x),
        plot_height=250,
        title="Fruit Counts by Year",
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

    script, div = components(plot)
    return script, div


def welcome(request):
    #profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = LogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('/logs/') #, {'profile': profile})
    else:
        form = LogForm()
    return render(request, 'logs/home.html', {'form': form}) #, 'profile': profile})
    return render(
        request,
        'logs/home.html',
        {'script': script, 'div': div}
    )
    # return render(request, 'logs/home.html')


def profile(request):
    user = Profile.objects.all()
    print(user)
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'logs/profile.html', {'profile': profile})


def logs2(request):
    print(request.user)
    logs = Log.objects.filter(user=request.user).order_by("date")
    return render(request, 'logs/logs.html', {'logs': logs})


def projects(request):
    projects = Project.objects.filter(user=request.user).order_by("created_at")
    counts = {
        p.title:
        Log.objects.filter(project=p, user=request.user).values('project').order_by('project').aggregate(Sum('count')) for p in projects
    }
    print(counts)
    return render(request, 'logs/projects.html', {'projects': projects, 'counts': counts})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, user=request.user)
    count = Log.objects.filter(project=project).aggregate(Sum('count'))
    return render(request, 'logs/project_detail.html', {'project': project, 'count': count})


def stats(request, mode="days"):
    if mode == "weeks":
        level = "Woche"
        # last 15 weeks
        # months = Log.objects.annotate(month_stamp=Extract('time_stamp', 'month')).values_list('month_stamp', flat=True)
        stats = Log.objects.annotate(level=Extract('date', 'week')).filter(user=request.user).values('level').order_by('date').annotate(total_count=Sum('count'))
    elif mode == "months":
        level = "Monat"
        # last 12 months
        stats = Log.objects.annotate(level=Extract('date', 'month')).filter(user=request.user).values('level').order_by('date').annotate(total_count=Sum('count'))
    elif mode == "years":
        level = "Jahr"
        # everything
        stats = Log.objects.annotate(level=Extract('date', 'year')).filter(user=request.user).values('level').order_by('date').annotate(total_count=Sum('count'))
    else:
        level = "Tag"
        # last 30 days
        stats = Log.objects.annotate(level=Extract('date', 'day')).filter(user=request.user).values('level').order_by('date').annotate(total_count=Sum('count'))
    script, div = chart(stats)
    return render(
        request,
        'logs/stats.html',
        {'script': script, 'div': div, 'stats': stats, 'level': level}
    )


def logs(request):
    print("hi")
    data = {}
    if "GET" == request.method:
        logs = Log.objects.filter(user=request.user).order_by("date")
        return render(request, 'logs/logs.html', {'logs': logs})
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
