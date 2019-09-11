from rq import Queue
from worker import conn

from django.shortcuts import render, redirect

from worker import conn
from .models import PontoonSyncLog, PontoonResource
from .sync import sync, sync_running


queue = Queue('wagtail_localize_pontoon.sync', connection=conn)


def dashboard(request):
    return render(request, 'wagtail_localize_pontoon/dashboard.html', {
        'resources': PontoonResource.objects.all(),
        'logs': PontoonSyncLog.objects.order_by('-time'),
        'sync_running': sync_running(),
        'sync_queued': bool(queue.get_jobs())
    })


def force_sync(request):
    if not sync_running():
        # Make sure there is only one job in the queue at a time
        queue.delete()
        queue.enqueue(sync)

    return redirect('wagtail_localize_pontoon:dashboard')
