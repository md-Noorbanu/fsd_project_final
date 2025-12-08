from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout

from myapp.forms import ReminderForm
from .models import Member, Reminder, ReminderHistory
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import datetime
from django.conf import settings
from django.db import connection
# Create your views here.
def homepage(request):
    return render(request, 'myapp/homepage.html')
def login(request):
    # handle logout via querystring
    if request.GET.get('logout'):
        auth_logout(request)
        return redirect('homepage')

    # handle POST login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # allow users to provide either username or email
        user = authenticate(request, username=username, password=password)
        if user is None:
            # if input looks like an email, try to resolve to username
            if username and '@' in username:
                try:
                    u = User.objects.get(email__iexact=username)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    user = None

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid credentials'})
    return render(request, 'myapp/login.html')
def dashboard(request):
    from .models import Member, Reminder

    # require login to view dashboard and scope to the logged-in user
    if not request.user.is_authenticated:
        return redirect('login')

    members = Member.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)

    context = {
        'members': members,
        'reminders': reminders
    }
    return render(request, 'myapp/dashboard.html', context)
def profile(request):
    member = None
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            member = None

    # handle profile update
    if request.method == 'POST' and request.user.is_authenticated:
        name = request.POST.get('name')
        age = request.POST.get('age')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # update user email
        if email:
            request.user.email = email
            request.user.save()

        # update or create member
        if member is None:
            member = Member.objects.create(user=request.user, name=name or request.user.username, age=age or 0, phone=phone or '')
        else:
            if name:
                member.name = name
            if age:
                try:
                    member.age = int(age)
                except ValueError:
                    pass
            if phone:
                member.phone = phone
            member.save()

        return redirect('profile')

    return render(request, 'myapp/profile.html', {'member': member})
def edit(request):
    return render(request, 'myapp/edit.html')

def delete(request):
    return render(request,'myapp/delete.html')
def reg(request):
    # Registration: create Django User and Member profile
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # if username hidden/empty, use email as username
        if not username:
            username = email.split('@')[0] if email else None
        name = request.POST.get('name') or username
        age = request.POST.get('age') or 0
        phone = request.POST.get('phone') or ''

        if not username:
            return render(request, 'myapp/reg.html', {'error': 'Username/email required'})

        if User.objects.filter(username=username).exists():
            return render(request, 'myapp/reg.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, email=email, password=password)
        member = Member.objects.create(user=user, name=name, age=age, phone=phone)
        auth_login(request, user)
        return redirect('profile')

    return render(request, 'myapp/reg.html')
def reminder(request):
    return render(request, 'myapp/reminder.html')
@login_required
def rempages(request):
    reminders = Reminder.objects.filter(user=request.user)
    return render(request, 'myapp/rempages.html', {'reminders': reminders})
@login_required
def add_reminder(request):
    form = ReminderForm()
    if request.method == 'POST':
        # Only logged-in users can add reminders. Use or create a Member for this user.
        post = request.POST.copy()
        member_name = post.get('member_name')
        if member_name:
            member_obj, created = Member.objects.get_or_create(user=request.user, defaults={'name': member_name})
            if created:
                member_obj.name = member_name
                member_obj.save()
            post['member'] = str(member_obj.id)

        form = ReminderForm(post)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return redirect('dashboard')
    return render(request, 'myapp/reminder.html', {'form': form})
@login_required
def editReminder(request, id):
    try:
        reminder = Reminder.objects.get(id=id, user=request.user)
    except Reminder.DoesNotExist:
        return redirect('dashboard')

    form = ReminderForm(request.POST or None, instance=reminder)
    if form.is_valid():
        rem = form.save(commit=False)
        rem.user = request.user
        rem.save()
        return redirect('dashboard')
    return render(request, "myapp/edit.html", {"form": form})


@login_required
def upcoming_reminders(request):
    """Return JSON list of upcoming reminders (not yet notified) for the logged-in user.

    Improvements:
    - use server local time via `timezone.localtime()` for comparisons
    - widen the look-ahead/past windows to be more forgiving (10 minutes)
    - add per-reminder debug logging to help diagnose timezone/ownership issues
    """
    # use localtime to match server clock used for stored datetimes
    now = timezone.localtime()
    # consider reminders within next 10 minutes to be tolerant of small clock skews
    window = now + datetime.timedelta(minutes=10)
    # also allow reminders slightly in the past (up to 10 minutes) to catch missed triggers
    past_window = now - datetime.timedelta(minutes=10)

    # normalize debug flag (accept '1', 'true', 'yes' case-insensitive)
    debug_mode = str(request.GET.get('debug', '')).strip().lower() in ('1', 'true', 'yes')

    # useful debug logging to observe when the endpoint is called and by whom
    try:
        import logging
        logger = logging.getLogger('myapp')
        logger.debug('upcoming_reminders called: user=%s debug=%s', request.user.username if hasattr(request.user, 'username') else str(request.user), debug_mode)
    except Exception:
        # best-effort: avoid crashing if logging isn't available
        print('upcoming_reminders called by', request.user, 'debug=', debug_mode)

    results = []
    # base queryset — for normal mode restrict to reminders owned by the logged-in user.
    # A reminder may be owned directly via `Reminder.user` or indirectly via `Reminder.member.user`.
    if debug_mode:
        reminders_qs = Reminder.objects.filter(notified=False)
    else:
        reminders_qs = Reminder.objects.filter(notified=False).filter(
            Q(user=request.user) | Q(member__user=request.user)
        )

    for r in reminders_qs:
        # combine date and time into a datetime
        try:
            dt = datetime.datetime.combine(r.date, r.time)
        except Exception:
            continue
        # make aware in server timezone if naive
        if timezone.is_naive(dt):
            try:
                dt = timezone.make_aware(dt, timezone.get_default_timezone())
            except Exception:
                # last resort: assume UTC
                dt = timezone.make_aware(dt, timezone.utc)
        # convert dt to server localtime for consistent comparisons
        try:
            dt = timezone.localtime(dt)
        except Exception:
            # if localtime conversion fails just leave dt as-is
            pass

        # compute flags used for debugging
        in_window = (past_window <= dt <= window)
        is_owner = (r.user_id == request.user.id) if request.user.is_authenticated else False

        if in_window or debug_mode:
            item = {
                'id': r.id,
                'title': r.medicine_name,
                'datetime': dt.isoformat(),
                'dosage': r.dosage,
                'computed_ts': dt.timestamp(),
                'server_now': now.isoformat(),
                'in_window': in_window,
                'is_owner': is_owner,
                'user_id': r.user_id,
            }
            results.append(item)
        # log details for each candidate so we can see why something was/wasn't selected
        try:
            import logging
            logger = logging.getLogger('myapp')
            logger.debug('reminder candidate: id=%s dt=%s in_window=%s owner=%s notified=%s', r.id, getattr(dt, 'isoformat', lambda: str(dt))(), in_window, is_owner, r.notified)
        except Exception:
            print('reminder candidate:', r.id, getattr(dt, 'isoformat', lambda: str(dt))(), 'in_window=', in_window, 'owner=', is_owner, 'notified=', r.notified)

    # log a concise summary to server console for debugging
    if results:
        try:
            import logging
            logger = logging.getLogger('myapp')
            logger.info('upcoming_reminders: found %d candidates for user=%s (debug=%s)', len(results), request.user.username if request.user.is_authenticated else 'anon', debug_mode)
        except Exception:
            print('upcoming_reminders: found', len(results), 'candidates; debug=', debug_mode)

    return JsonResponse({'reminders': results, 'debug': debug_mode, 'count': len(results)})


@login_required
@require_POST
def mark_reminder_notified(request, id):
    try:
        # allow marking a reminder as notified if the logged-in user is the owner
        # either via Reminder.user or Reminder.member.user
        r = Reminder.objects.get(Q(id=id) & (Q(user=request.user) | Q(member__user=request.user)))
    except Reminder.DoesNotExist:
        return HttpResponseBadRequest('invalid reminder')
    r.notified = True
    r.save()
    return JsonResponse({'status': 'ok'})
@login_required
def deleteReminder(request, id):
    try:
        reminder = Reminder.objects.get(id=id, user=request.user)
        reminder.delete()
    except Reminder.DoesNotExist:
        # ignore attempts to delete non-owned reminders
        pass
    return redirect('dashboard')
def viewReminders(request):
    # show only reminders for the logged-in user
    if not request.user.is_authenticated:
        return redirect('login')
    data = Reminder.objects.filter(user=request.user)
    return render(request, "myapp/rempages.html", {"reminders": data})


def db_status(request):
    """Diagnostic: show which database Django is connected to and list recent users.

    Use this page to confirm registration/login data are persisted to the configured database.
    """
    info = {}
    try:
        info['configured'] = settings.DATABASES.get('default', {})
    except Exception:
        info['configured'] = 'unavailable'

    try:
        with connection.cursor() as cur:
            cur.execute('SELECT DATABASE()')
            dbname = cur.fetchone()[0]
        info['connected_database'] = dbname
    except Exception as e:
        info['connected_database'] = f'error: {e}'

    try:
        users = list(User.objects.all().order_by('-id').values('id', 'username', 'email')[:10])
        info['recent_users'] = users
        info['user_count'] = User.objects.count()
    except Exception as e:
        info['recent_users'] = f'error: {e}'
        info['user_count'] = 'error'

    return JsonResponse(info)
from django.http import JsonResponse
from .models import Reminder
from django.utils import timezone

def get_due_reminders(request):
    now = timezone.localtime()
    current_date = now.date()
    current_time = now.time()

    # find reminders matching today's date and a time up to the current minute
    # (exact time match is brittle, so accept reminders whose time is <= current_time)
    reminders = Reminder.objects.filter(date=current_date, notified=False)

    result = []
    for r in reminders:
        try:
            # include reminders whose scheduled time is <= now
            if r.time <= current_time:
                result.append({
                    "id": r.id,
                    "title": r.medicine_name,
                    "dosage": r.dosage,
                    "member": r.member.name if r.member else None,
                })
        except Exception:
            continue

    return JsonResponse({"reminders": result})


@login_required
def all_user_reminders(request):
    """Return all reminders for the logged-in user (owned via Reminder.user or member.user).

    Useful for debugging and for forcing notifications from the browser UI.
    """
    from django.db.models import Q
    reminders = Reminder.objects.filter(Q(user=request.user) | Q(member__user=request.user))
    out = []
    for r in reminders:
        out.append({
            'id': r.id,
            'title': r.medicine_name,
            'date': str(r.date),
            'time': str(r.time),
            'dosage': r.dosage,
            'notified': r.notified,
            'member': r.member.name if r.member else None,
        })
    return JsonResponse({'reminders': out, 'count': len(out)})