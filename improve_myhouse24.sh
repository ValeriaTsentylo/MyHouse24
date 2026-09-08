#!/usr/bin/env bash
#
# improve_myhouse24.sh — приводить репозиторій MyHouse24 до стану,
# який не соромно дати рекрутеру / технічному інтерв'юеру.
#
# Запуск з кореня репозиторію:
#     chmod +x improve_myhouse24.sh
#     ./improve_myhouse24.sh
#
# Скрипт:
#   * створює окрему гілку improve/repo-audit (main не чіпає);
#   * робить окремий коміт на кожен логічний крок;
#   * ідемпотентний — повторний запуск нічого не ламає;
#   * якщо якийсь анкер у коді не знайдено, друкує WARN і йде далі.
#
set -euo pipefail

BRANCH="improve/repo-audit"
WARNINGS=0

c_ok()   { printf '\033[32m  ✓\033[0m %s\n' "$1"; }
c_skip() { printf '\033[90m  ·\033[0m %s\n' "$1"; }
c_warn() { printf '\033[33m  ! WARN\033[0m %s\n' "$1"; WARNINGS=$((WARNINGS+1)); }
c_step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
die()    { printf '\033[31mПОМИЛКА:\033[0m %s\n' "$1" >&2; exit 1; }

commit() {
  git add -A
  if git diff --cached --quiet; then
    c_skip "нема змін для коміту"
  else
    git commit -q -m "$1"
    c_ok "commit: $1"
  fi
}

# ─────────────────────────────────────────────────────────────
# 0. Перевірки
# ─────────────────────────────────────────────────────────────
c_step "Перевірки"

command -v git >/dev/null     || die "git не знайдено"
command -v python3 >/dev/null || die "python3 не знайдено"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "це не git-репозиторій"
cd "$ROOT"

[ -f manage.py ] && [ -d src ] && [ -f config/settings.py ] \
  || die "не схоже на MyHouse24 (немає manage.py / src / config/settings.py)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  die "робоче дерево брудне. Закомить або сховай зміни (git stash) і запусти знову."
fi

if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
  git switch -c "$BRANCH" 2>/dev/null || git switch "$BRANCH"
fi
c_ok "гілка: $BRANCH"

# ─────────────────────────────────────────────────────────────
# 1. Прибрати з git артефакти збірки та сміття
# ─────────────────────────────────────────────────────────────
c_step "1/9 Чистка репозиторію"

python3 - <<'PY'
from pathlib import Path

WANT = [
    "# env", ".env", ".env_local", ".env_prod", ".env.test", "",
    "# virtual env", ".venv/", "venv/", "/.idea", "/.vscode", "",
    "# python", "__pycache__/", "*.py[cod]", ".pytest_cache/",
    ".coverage", "htmlcov/", "",
    "# django build artifacts", "/staticfiles/", "/media/", "",
    "# vendor source maps (не потрібні в рантаймі)", "*.map", "",
    "# os", ".DS_Store",
]
p = Path(".gitignore")
cur = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
have = {l.strip() for l in cur if l.strip()}
add = [l for l in WANT if not l.strip() or l.strip() not in have]
# прибираємо дублікати порожніх рядків на стику
while add and not add[0].strip():
    add.pop(0)
if add:
    out = "\n".join(cur).rstrip() + "\n\n" + "\n".join(add).rstrip() + "\n"
    p.write_text(out, encoding="utf-8")
    print("  .gitignore оновлено")
else:
    print("  .gitignore уже актуальний")
PY

# staticfiles/ — це STATIC_ROOT, результат collectstatic. У git йому не місце.
if git ls-files --error-unmatch staticfiles >/dev/null 2>&1; then
  git rm -r --cached -q staticfiles
  c_ok "staticfiles/ прибрано з індексу"
else
  c_skip "staticfiles/ уже не відстежується"
fi

# media/ — це користувацькі завантаження, не код
if git ls-files --error-unmatch media >/dev/null 2>&1; then
  git rm -r --cached -q media
  c_ok "media/ прибрано з індексу"
fi

# скомпільовані .pyc, які просочились у перший коміт
PYC_BEFORE=$(git ls-files | grep -c '__pycache__' || true)
if [ "${PYC_BEFORE:-0}" != "0" ]; then
  git rm -r --cached -q --ignore-unmatch '*__pycache__*'
  c_ok "__pycache__ прибрано з індексу ($PYC_BEFORE файлів)"
else
  c_skip "__pycache__ не відстежується"
fi

# source maps вендорного AdminLTE — ~32 МБ, у рантаймі не потрібні
MAPS=$(find static -name '*.map' -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$MAPS" != "0" ]; then
  find static -name '*.map' -type f -delete
  c_ok "видалено $MAPS source map'ів зі static/"
fi

commit "chore: stop tracking build artifacts and vendor source maps

- staticfiles/ is a collectstatic artifact and does not belong in VCS
- media/ holds runtime user uploads
- drop committed __pycache__ and ~32 MB of vendor .map files"

# ─────────────────────────────────────────────────────────────
# 2. Безпека: міксини доступу
# ─────────────────────────────────────────────────────────────
c_step "2/9 Контроль доступу до в'юх"

mkdir -p src/core
cat > src/core/mixins.py <<'EOF'
"""Reusable access-control mixins.

The project defines custom permissions on ``users.User.Meta.permissions`` and a
``User.has_permission()`` helper; these mixins are what actually enforce them on
class-based views.
"""

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(AccessMixin):
    """Allow only authenticated staff members.

    Set ``required_permission`` on a view to additionally require one of the
    custom permissions declared on the ``User`` model, e.g.::

        class HousesListView(StaffRequiredMixin, TemplateView):
            required_permission = "view_houses"
    """

    required_permission: str | None = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied("Staff access required.")

        if (
            self.required_permission
            and not user.is_superuser
            and not user.has_permission(self.required_permission)
        ):
            raise PermissionDenied(f"Missing permission: {self.required_permission}")

        return super().dispatch(request, *args, **kwargs)


class ResidentRequiredMixin(AccessMixin):
    """Allow any authenticated user (resident cabinet pages)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
EOF
c_ok "створено src/core/mixins.py"

python3 - <<'PY'
import re
from pathlib import Path

DJANGO_BASES = {
    "View", "TemplateView", "FormView", "ListView", "DetailView",
    "UpdateView", "CreateView", "DeleteView", "AjaxDatatableView",
}
# автентифікація має лишатись доступною анонімам
SKIP = {"login_view.py", "sign_up_view.py", "logout_view.py"}
# сторінки мешканця: досить залогіненого користувача, не staff
RESIDENT = {"user_profile_view.py", "users_dashboard_view.py"}

MIXINS = {
    "staff": ("StaffRequiredMixin", "from src.core.mixins import StaffRequiredMixin"),
    "resident": ("ResidentRequiredMixin", "from src.core.mixins import ResidentRequiredMixin"),
}

files = sorted(set(Path("src").glob("*/views/*.py")) | set(Path("src").glob("*/views.py")))
patched, already = 0, 0

for f in files:
    if f.name in SKIP or f.name == "__init__.py":
        continue
    kind = "resident" if f.name in RESIDENT else "staff"
    mixin, import_line = MIXINS[kind]

    text = f.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False

    for i, line in enumerate(lines):
        m = re.match(r"^class (\w+)\(([^)]*)\):\s*$", line)
        if not m:
            continue
        name, bases = m.group(1), m.group(2)
        base_names = {b.strip().split(".")[-1] for b in bases.split(",") if b.strip()}
        if not (base_names & DJANGO_BASES):
            continue
        if "RequiredMixin" in bases:
            already += 1
            continue
        lines[i] = f"class {name}({mixin}, {bases}):\n"
        changed = True

    if not changed:
        continue

    if import_line not in text:
        depth, last_end = 0, -1
        for i, line in enumerate(lines):
            s = line.strip()
            if depth == 0 and not (s.startswith("from ") or s.startswith("import ")):
                if s.startswith(("class ", "def ", "@")):
                    break
                continue
            depth += line.count("(") - line.count(")")
            if depth <= 0:
                depth, last_end = 0, i
        if last_end >= 0:
            lines.insert(last_end + 1, import_line + "\n")
        else:
            lines.insert(0, import_line + "\n\n")

    f.write_text("".join(lines), encoding="utf-8")
    patched += 1

print(f"  захищено в'юх у {patched} файлах, вже було захищено класів: {already}")
print(f"  свідомо пропущено (публічні): {', '.join(sorted(SKIP))}")
PY

# src/core/views.py — функційна в'юха, яку міксин-пас не бачить:
# рендерить адмінську оболонку AdminLTE будь-якому анонімові
python3 - <<'PYCORE'
from pathlib import Path

p = Path("src/core/views.py")
if not p.exists():
    print("  ! WARN: немає src/core/views.py")
else:
    t = p.read_text(encoding="utf-8")
    if "login_required" in t:
        print("  · src/core/views.py уже захищено")
    elif "def index(request):" in t:
        t = t.replace(
            "from django.shortcuts import render\n",
            "from django.contrib.auth.decorators import login_required, user_passes_test\n"
            "from django.shortcuts import render\n",
            1,
        )
        t = t.replace(
            "def index(request):",
            "@login_required\n"
            "@user_passes_test(lambda u: u.is_staff or u.is_superuser)\n"
            "def index(request):",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("  index() у src/core/views.py: login_required + staff-перевірка")
    else:
        print("  ! WARN: не знайшов index() у src/core/views.py")
PYCORE

# has_permission() падав з AttributeError, коли role is None (а поле nullable)
python3 - <<'PY'
from pathlib import Path

p = Path("src/users/models.py")
t = p.read_text(encoding="utf-8")
old = '''        return self.role.permissions.filter(codename=perm_codename).exists()'''
new = '''        if self.is_superuser:
            return True
        if not self.role_id:
            return False
        return self.role.permissions.filter(codename=perm_codename).exists()'''
if new in t:
    print("  User.has_permission уже пофікшено")
elif old in t:
    p.write_text(t.replace(old, new), encoding="utf-8")
    print("  User.has_permission: додано перевірку role is None + superuser")
else:
    print("  ! WARN: не знайшов тіло User.has_permission — перевір вручну")
PY

commit "fix(security): enforce authentication and staff access on all views

Every class-based view was reachable anonymously, including staff-only
CRUD for users, houses, apartments and tariffs. Adds StaffRequiredMixin /
ResidentRequiredMixin (wired to the custom permissions already declared on
the User model) and applies them across the view layer.

Also makes User.has_permission() safe when the user has no role assigned."

# ─────────────────────────────────────────────────────────────
# 3. Безпека: settings.py та urls.py
# ─────────────────────────────────────────────────────────────
c_step "3/9 Налаштування Django"

python3 - <<'PY'
from pathlib import Path

p = Path("config/settings.py")
t = p.read_text(encoding="utf-8")
orig = t
notes = []

def sub(old, new, note):
    global t
    if new in t:
        return
    if old in t:
        t = t.replace(old, new, 1)
        notes.append(note)
    else:
        notes.append(f"! WARN: анкер не знайдено — {note}")

# DEBUG за замовчуванням має бути вимкнений
sub('DEBUG = config("DEBUG", default=True, cast=bool)',
    'DEBUG = config("DEBUG", default=False, cast=bool)',
    "DEBUG default=False")

# debug_toolbar більше не вантажиться безумовно
t = t.replace('    "debug_toolbar",\n', "", 1)
t = t.replace('    "debug_toolbar.middleware.DebugToolbarMiddleware",\n', "", 1)

anchor = 'INTERNAL_IPS = [\n    "127.0.0.1",\n]\n'
djdt = (anchor + '\n'
        '# debug_toolbar is a development-only dependency\n'
        'if DEBUG:\n'
        '    INSTALLED_APPS += ["debug_toolbar"]\n'
        '    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")\n')
if "if DEBUG:\n    INSTALLED_APPS += " not in t:
    if anchor in t:
        t = t.replace(anchor, djdt, 1)
        notes.append("debug_toolbar тільки під if DEBUG")
    else:
        notes.append("! WARN: не знайшов INTERNAL_IPS — debug_toolbar не перенесено")

# локаль проєкту
sub('LANGUAGE_CODE = "en-us"', 'LANGUAGE_CODE = "uk"', 'LANGUAGE_CODE = "uk"')
sub('TIME_ZONE = "UTC"', 'TIME_ZONE = "Europe/Kyiv"', 'TIME_ZONE = Europe/Kyiv')

# брокер celery з оточення, а не хардкод
sub('CELERY_BROKER_URL = "redis://localhost:6379/0"  # Use Redis as the broker',
    'CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")\n'
    'CELERY_RESULT_BACKEND = CELERY_BROKER_URL',
    "CELERY_BROKER_URL з оточення")

# проєкт має підніматись без повного .env (тести, CI, перший клон)
for old, new, note in [
    ('EMAIL_HOST = config("EMAIL_HOST")',
     'EMAIL_HOST = config("EMAIL_HOST", default="localhost")', "EMAIL_HOST default"),
    ('EMAIL_PORT = config("EMAIL_PORT", cast=int)',
     'EMAIL_PORT = config("EMAIL_PORT", cast=int, default=25)', "EMAIL_PORT default"),
    ('EMAIL_HOST_USER = config("EMAIL_HOST_USER")',
     'EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")', "EMAIL_HOST_USER default"),
    ('EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")',
     'EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")', "EMAIL_HOST_PASSWORD default"),
    ('EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)',
     'EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)', "EMAIL_USE_TLS default"),
    ('RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY")',
     'RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY", default="")', "RECAPTCHA_PUBLIC_KEY default"),
    ('RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY")',
     'RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY", default="")', "RECAPTCHA_PRIVATE_KEY default"),
    ('SECRET_KEY = config("SECRET_KEY")',
     'SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key-change-me")',
     "SECRET_KEY dev-default"),
    ('"NAME": config("DB_NAME"),', '"NAME": config("DB_NAME", default="myhouse24"),', "DB_NAME default"),
    ('"USER": config("DB_USER"),', '"USER": config("DB_USER", default="myhouse24"),', "DB_USER default"),
    ('"PASSWORD": config("DB_PASSWORD"),',
     '"PASSWORD": config("DB_PASSWORD", default="myhouse24"),', "DB_PASSWORD default"),
]:
    sub(old, new, note)

MARKER = "# --- Security / logging hardening ---"
if MARKER not in t:
    t = t.rstrip() + '\n\n' + MARKER + '''
# Everything below is inert during local development and turns on in production.

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "src": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}
'''
    notes.append("додано блок hardening + LOGGING")

if t != orig:
    p.write_text(t, encoding="utf-8")
for n in notes:
    print("  " + n)
PY

python3 - <<'PY'
from pathlib import Path

p = Path("config/urls.py")
t = p.read_text(encoding="utf-8")
orig = t

MARKER = 'urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]'
old_tail = ('if settings.DEBUG:\n'
            '    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\n')
new_tail = ('if settings.DEBUG:\n'
            '    import debug_toolbar\n\n'
            '    ' + MARKER + '\n'
            '    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\n')

if MARKER in t:
    print("  config/urls.py уже пофікшено")
else:
    t = t.replace("import debug_toolbar\n", "", 1)
    t = t.replace('    path("__debug__/", include(debug_toolbar.urls)),\n', "", 1)
    if old_tail in t:
        t = t.replace(old_tail, new_tail, 1)
        print("  config/urls.py: debug_toolbar тільки під DEBUG")
    else:
        print("  ! WARN: не знайшов хвіст config/urls.py — перевір вручну")
        t = orig

if t != orig:
    p.write_text(t, encoding="utf-8")
PY

commit "fix(settings): production-safe defaults and dev-only tooling

- DEBUG defaults to False instead of True
- debug_toolbar app, middleware and URLs load only when DEBUG
- HSTS, SSL redirect, secure cookies, nosniff, X-Frame-Options for prod
- Celery broker read from REDIS_URL instead of a hardcoded localhost
- sane defaults so the project boots without a fully populated .env
- structured LOGGING config; locale switched to uk / Europe/Kyiv"

# ─────────────────────────────────────────────────────────────
# 4. Точкові правки коду
# ─────────────────────────────────────────────────────────────
c_step "4/9 Точкові правки коду"

python3 - <<'PY'
import re
from pathlib import Path

report = []

def patch(path, old, new, note, marker=None):
    p = Path(path)
    if not p.exists():
        report.append(f"! WARN: немає {path}")
        return
    t = p.read_text(encoding="utf-8")
    if (marker or new) in t:
        report.append(f"· {note} — вже зроблено")
        return
    if old not in t:
        report.append(f"! WARN: анкер не знайдено — {note} ({path})")
        return
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    report.append(f"✓ {note}")

# --- N+1 у дататейблі квартир: 4 колонки тягнуть FK по рядку ---
patch(
    "src/apartments/views/apartments_database_view.py",
    "        queryset = super().get_initial_queryset(request)\n",
    '        queryset = super().get_initial_queryset(request).select_related(\n'
    '            "house", "section", "floor", "owner"\n'
    '        )\n',
    "select_related у ApartmentsAjaxDatatableView (N+1)",
    marker='.select_related(\n            "house", "section", "floor", "owner"',
)

# --- увесь список користувачів у контексті сторінки ---
patch(
    "src/apartments/views/apartments_database_view.py",
    '        context["users"] = User.objects.all()\n',
    '        context["users"] = User.objects.filter(is_staff=False).only(\n'
    '            "id", "name", "email"\n'
    '        )\n',
    "звужено вибірку користувачів у ApartmentsListView",
)

# --- створення staff-користувача: два save(), відсутня транзакція,
#     celery-таска може стартувати до коміту транзакції ---
patch(
    "src/users/views/create_staff_user_view.py",
    """        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password1"]

            user.set_password(password)
            user.is_staff = True

            user.save()

            role = form.cleaned_data["role"]
            user.role = role
            user.save()
""",
    """        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password1"]

            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(password)
                user.is_staff = True
                user.role = form.cleaned_data["role"]
                user.save()
""",
    "CreateStaffUserView: один save() всередині transaction.atomic",
    marker="with transaction.atomic():",
)
patch(
    "src/users/views/create_staff_user_view.py",
    """            send_email_task.delay(
                subject, "emails_template/account_create.html", context, user.email
            )
""",
    """            transaction.on_commit(
                lambda: send_email_task.delay(
                    subject, "emails_template/account_create.html", context, user.email
                )
            )
""",
    "CreateStaffUserView: лист відправляється через transaction.on_commit",
    marker="transaction.on_commit(",
)
patch(
    "src/users/views/create_staff_user_view.py",
    "from django.shortcuts import render, redirect\n",
    "from django.db import transaction\nfrom django.shortcuts import render, redirect\n",
    "CreateStaffUserView: імпорт transaction",
    marker="from django.db import transaction",
)

# --- створення будинку: get_context_data() двічі + немає транзакції ---
patch(
    "src/houses/views/create_house_view.py",
    """        if (
            section_formset.is_valid()
            and floor_formset.is_valid()
            and staff_formset.is_valid()
        ):
            house = form.save()

            section_formset.instance = house
            floor_formset.instance = house
            staff_formset.instance = house

            section_formset.save()
            floor_formset.save()
            staff_formset.save()

            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))
""",
    """        if not (
            section_formset.is_valid()
            and floor_formset.is_valid()
            and staff_formset.is_valid()
        ):
            return self.render_to_response(context)

        with transaction.atomic():
            house = form.save()
            for formset in (section_formset, floor_formset, staff_formset):
                formset.instance = house
                formset.save()

        return redirect(self.success_url)
""",
    "CreateHouseView: transaction.atomic + без повторного get_context_data",
    marker="with transaction.atomic():",
)
patch(
    "src/houses/views/create_house_view.py",
    "from django.shortcuts import redirect\n",
    "from django.db import transaction\nfrom django.shortcuts import get_object_or_404, redirect\n",
    "CreateHouseView: імпорти transaction / get_object_or_404",
    marker="from django.db import transaction",
)
patch(
    "src/houses/views/create_house_view.py",
    "            return House.objects.get(pk=house_id)\n",
    "            return get_object_or_404(House, pk=house_id)\n",
    "CreateHouseView: get_object_or_404 замість .get()",
)

# --- мертвий код: функція зі self поза класом і role.all() на FK ---
p = Path("src/users/utils.py")
if p.exists():
    t = p.read_text(encoding="utf-8")
    i = t.find("def send_admin_account_email(")
    if i == -1:
        report.append("· мертвий send_admin_account_email — уже видалено")
    else:
        p.write_text(t[:i].rstrip() + "\n", encoding="utf-8")
        report.append("✓ видалено мертвий send_admin_account_email() (self поза класом, role.all() на FK)")

# --- print() -> logging ---
def split_args(s):
    depth, cur, out = 0, "", []
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out

PRINT_RE = re.compile(r"^(\s*)print\((.*)\)\s*(#.*)?$")
converted = 0
for f in Path("src").rglob("*.py"):
    if "migrations" in f.parts:
        continue
    lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        m = PRINT_RE.match(line.rstrip("\n"))
        if not m:
            continue
        indent, args = m.group(1), m.group(2)
        parts = split_args(args)
        if len(parts) == 1:
            call = f"{indent}logger.warning({parts[0]})\n"
        else:
            fmt = parts[0].rstrip('"\'') + " " + " ".join(["%s"] * (len(parts) - 1))
            if not parts[0].startswith(("'", '"')):
                fmt = " ".join(["%s"] * len(parts))
                call = f'{indent}logger.warning("{fmt}", {", ".join(parts)})\n'
            else:
                quote = parts[0][0]
                call = f'{indent}logger.warning({quote}{parts[0].strip(quote)} ' \
                       f'{" ".join(["%s"] * (len(parts) - 1))}{quote}, {", ".join(parts[1:])})\n'
        lines[i] = call
        changed = True
        converted += 1
    if changed:
        text = "".join(lines)
        if "logger = logging.getLogger(__name__)" not in text:
            for i, line in enumerate(lines):
                if line.startswith(("class ", "def ")):
                    lines.insert(i, "logger = logging.getLogger(__name__)\n\n\n")
                    break
            lines.insert(0, "import logging\n\n")
        f.write_text("".join(lines), encoding="utf-8")
if converted:
    report.append(f"✓ замінено {converted} print() на logger.warning()")
else:
    report.append("· print() не знайдено")

for line in report:
    print("  " + line)
PY

commit "refactor: fix N+1, transaction safety and leftovers in the view layer

- select_related on the apartments datatable (4 FK columns per row)
- narrow the user queryset fed into the apartments page context
- wrap staff-user and house creation in transaction.atomic
- fire the Celery email task from transaction.on_commit, not mid-transaction
- get_object_or_404 instead of a bare .get()
- drop dead send_admin_account_email() (stray self, .all() on a FK)
- replace print() debugging with module loggers"

# ─────────────────────────────────────────────────────────────
# 5. Docker
# ─────────────────────────────────────────────────────────────
c_step "5/9 Docker"

cat > Dockerfile <<'EOF'
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==1.8.5"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

cat > .dockerignore <<'EOF'
.git
.github
.venv
venv
__pycache__
*.py[cod]
.pytest_cache
staticfiles
media
.env
.env_local
.env_prod
*.md
!README.md
EOF

cat > docker-compose.yml <<'EOF'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-myhouse24}
      POSTGRES_USER: ${DB_USER:-myhouse24}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-myhouse24}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-myhouse24}"]
      interval: 5s
      retries: 10
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 10

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    env_file: [.env_local]
    environment:
      DB_HOST: db
      REDIS_URL: redis://redis:6379/0
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      db: {condition: service_healthy}
      redis: {condition: service_healthy}

  celery:
    build: .
    command: celery -A config worker -l info
    env_file: [.env_local]
    environment:
      DB_HOST: db
      REDIS_URL: redis://redis:6379/0
    volumes:
      - .:/app
    depends_on:
      db: {condition: service_healthy}
      redis: {condition: service_healthy}

volumes:
  pgdata:
EOF

cat > .env.example <<'EOF'
# Скопіюй у .env_local і заповни
ENVIRONMENT=local
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=myhouse24
DB_USER=myhouse24
DB_PASSWORD=myhouse24
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

# Порожні значення = листи друкуються в консоль (DEBUG=True)
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True

RECAPTCHA_PUBLIC_KEY=
RECAPTCHA_PRIVATE_KEY=
EOF

c_ok "Dockerfile, docker-compose.yml, .dockerignore, .env.example"
commit "build: add Docker setup for the full stack

Postgres + Redis + Django + Celery worker, so the project can be brought
up with a single 'docker compose up'. Adds .env.example documenting every
setting the app reads."

# ─────────────────────────────────────────────────────────────
# 6. Тести
# ─────────────────────────────────────────────────────────────
c_step "6/9 Тести"

mkdir -p tests
cat > tests/__init__.py <<'EOF'
EOF

cat > tests/conftest.py <<'EOF'
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def _make_user(email, **extra):
    user = User(email=email, about_me="", **extra)
    user.set_password("pass12345")
    user.save()
    return user


@pytest.fixture
def resident(db):
    return _make_user("resident@example.com", name="Resident")


@pytest.fixture
def staff_user(db):
    return _make_user("staff@example.com", name="Staff", is_staff=True)


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user)
    return client
EOF

cat > tests/test_access_control.py <<'EOF'
"""Every admin view must reject anonymous visitors.

The test walks the real URLConf instead of a hardcoded list, so a newly added
view is covered the moment it is registered.
"""

import pytest
from django.urls import NoReverseMatch, URLPattern, URLResolver, get_resolver, reverse

# Public by design: auth flows, Django admin, dev tooling, static/media.
PUBLIC_PREFIXES = ("/admin/", "/users/accounts/", "/__debug__/", "/static/", "/media/")
PUBLIC_NAMES = {"account_login", "register", "account_logout"}


def _named_urls():
    urls = []

    def walk(patterns, prefix=""):
        for p in patterns:
            if isinstance(p, URLResolver):
                walk(p.url_patterns, prefix + str(p.pattern))
            elif isinstance(p, URLPattern) and p.name:
                urls.append((p.name, prefix + str(p.pattern)))

    walk(get_resolver().url_patterns)
    return urls


def _reverse(name, pattern):
    for kwargs in ({}, {"pk": 1}, {"house_id": 1}, {"user_id": 1}, {"apartment_id": 1}):
        try:
            return reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            continue
    return None


PROTECTED = sorted(
    {
        (name, url)
        for name, pattern in _named_urls()
        if name not in PUBLIC_NAMES
        and (url := _reverse(name, pattern))
        and not url.startswith(PUBLIC_PREFIXES)
    }
)


def test_url_discovery_found_views():
    assert PROTECTED, "URLConf walk returned nothing — the test itself is broken"


@pytest.mark.django_db
@pytest.mark.parametrize("name,url", PROTECTED, ids=[n for n, _ in PROTECTED])
def test_anonymous_cannot_reach_admin_views(client, name, url):
    # secure=True so an enabled SECURE_SSL_REDIRECT cannot mask the result
    response = client.get(url, secure=True)
    assert response.status_code in (302, 403), (
        f"{name} ({url}) returned {response.status_code} to an anonymous user"
    )
    if response.status_code == 302:
        assert "login" in response["Location"], (
            f"{name} redirected to {response['Location']} instead of the login page"
        )
EOF

cat > tests/test_users.py <<'EOF'
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from src.roles.models import RolePermission

User = get_user_model()


@pytest.mark.django_db
def test_str_falls_back_to_email():
    user = User.objects.create(email="no-name@example.com", about_me="")
    assert str(user) == "no-name@example.com"

    user.name = "Валерія"
    assert str(user) == "Валерія"


@pytest.mark.django_db
def test_has_permission_without_role_does_not_raise():
    """Regression: role is nullable, so this used to blow up with AttributeError."""
    user = User.objects.create(email="roleless@example.com", about_me="")
    assert user.has_permission("view_houses") is False


@pytest.mark.django_db
def test_superuser_bypasses_role_permissions():
    user = User.objects.create(email="root@example.com", about_me="", is_superuser=True)
    assert user.has_permission("view_houses") is True


@pytest.mark.django_db
def test_role_permission_is_scoped_to_the_assigned_role():
    role = RolePermission.objects.create(name="manager")
    user = User.objects.create(email="manager@example.com", about_me="", role=role)
    assert user.has_permission("view_houses") is False


@pytest.mark.django_db
def test_email_is_unique():
    User.objects.create(email="dup@example.com", about_me="")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(email="dup@example.com", about_me="")
EOF

# приберемо порожні заглушки tests.py
find src -name tests.py -size -1k -exec grep -lq "Create your tests here" {} \; -delete 2>/dev/null || true
for f in $(grep -rl "Create your tests here" src --include=tests.py 2>/dev/null || true); do rm -f "$f"; done
c_ok "tests/ (access control + модель User), заглушки tests.py прибрано"

python3 - <<'PY'
from pathlib import Path

p = Path("pyproject.toml")
t = p.read_text(encoding="utf-8")

if "pytest-django" not in t:
    t = t.replace(
        '[tool.poetry.group.dev.dependencies]\npre-commit = "^4.0.1"',
        '[tool.poetry.group.dev.dependencies]\n'
        'pre-commit = "^4.0.1"\n'
        'pytest = "^8.3.3"\n'
        'pytest-django = "^4.9.0"\n'
        'pytest-cov = "^6.0.0"\n'
        'ruff = "^0.8.0"\n'
        'djlint = "^1.36.1"',
        1,
    )

if "[tool.pytest.ini_options]" not in t:
    t = t.rstrip() + '''

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["test_*.py"]
addopts = "-q --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py312"
exclude = ["*/migrations/*", "static", "staticfiles"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "DJ"]
ignore = ["E501"]

[tool.djlint]
profile = "django"
ignore = "H006,H021,H030,H031"
'''
p.write_text(t, encoding="utf-8")
print("  pyproject.toml: dev-залежності + конфіги pytest / ruff / djlint")
PY

commit "test: add a baseline test suite

- tests/test_access_control.py walks the live URLConf and asserts every
  non-public view rejects anonymous requests, so new views are covered
  automatically
- tests/test_users.py covers User.__str__ and the has_permission() paths,
  including the nullable-role regression
- pytest/ruff/djlint configuration; removes the eight empty tests.py stubs"

# ─────────────────────────────────────────────────────────────
# 7. CI + pre-commit
# ─────────────────────────────────────────────────────────────
c_step "7/9 CI та pre-commit"

mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: myhouse24
          POSTGRES_USER: myhouse24
          POSTGRES_PASSWORD: myhouse24
        options: >-
          --health-cmd pg_isready --health-interval 5s --health-timeout 5s --health-retries 10
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]

    env:
      ENVIRONMENT: ci
      DEBUG: "True"
      SECRET_KEY: ci-secret-key
      ALLOWED_HOSTS: localhost,127.0.0.1,testserver
      DB_NAME: myhouse24
      DB_USER: myhouse24
      DB_PASSWORD: myhouse24
      DB_HOST: localhost
      DB_PORT: "5432"
      REDIS_URL: redis://localhost:6379/0

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Poetry
        run: pipx install poetry==1.8.5

      - name: Install dependencies
        run: poetry install --with dev --no-root

      - name: Lint
        run: |
          poetry run ruff check .
          poetry run ruff format --check .

      - name: Django checks
        run: poetry run python manage.py check

      - name: Missing migrations
        run: poetry run python manage.py makemigrations --check --dry-run

      - name: Tests
        run: poetry run pytest --cov=src --cov-report=term-missing
EOF

cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/djlint/djLint
    rev: v1.36.1
    hooks:
      - id: djlint-django
EOF

c_ok ".github/workflows/ci.yml + .pre-commit-config.yaml"
commit "ci: add GitHub Actions pipeline and restore pre-commit config

Runs ruff, django check, a missing-migrations check and pytest against
real Postgres and Redis services. check-added-large-files guards against
another 90 MB of build artifacts landing in the repo."

# ─────────────────────────────────────────────────────────────
# 8. Taskfile
# ─────────────────────────────────────────────────────────────
c_step "8/9 Taskfile"

python3 - <<'PY'
import re
from pathlib import Path

p = Path("Taskfile.yml")
if not p.exists():
    print("  ! WARN: Taskfile.yml не знайдено")
else:
    t = p.read_text(encoding="utf-8")
    # 'git add .' у таску — саме так у репо і опинились staticfiles та .idea
    t = re.sub(r"\n  git_push:.*?(?=\n  \w|\Z)", "\n", t, flags=re.S)
    extra = """
  up:
    desc: Start the whole stack (web, db, redis, celery) in Docker
    cmds:
      - docker compose up --build

  down:
    desc: Stop the stack
    cmds:
      - docker compose down

  test:
    desc: Run the test suite
    cmds:
      - poetry run pytest --cov=src --cov-report=term-missing

  lint:
    desc: Lint and format
    cmds:
      - poetry run ruff check --fix .
      - poetry run ruff format .

  check:
    desc: Django system checks, including deployment warnings
    cmds:
      - poetry run python manage.py check --deploy

  celery:
    desc: Start a Celery worker
    cmds:
      - poetry run celery -A config worker -l info
"""
    if "  test:" not in t:
        t = t.rstrip() + "\n" + extra
    p.write_text(t, encoding="utf-8")
    print("  прибрано таску git_push ('git add .'), додано up/down/test/lint/check/celery")
PY

commit "chore(taskfile): drop the 'git add .' push task, add dev shortcuts

The git_push task is how staticfiles/ and .idea/ ended up committed."

# ─────────────────────────────────────────────────────────────
# 9. Документація
# ─────────────────────────────────────────────────────────────
c_step "9/9 README та docs"

mkdir -p docs/screenshots
if [ -f DB_schema.png ] && [ ! -f docs/DB_schema.png ]; then
  git mv DB_schema.png docs/DB_schema.png 2>/dev/null || mv DB_schema.png docs/DB_schema.png
  c_ok "DB_schema.png → docs/"
fi
touch docs/screenshots/.gitkeep

cat > README.md <<'EOF'
# MyHouse24

Property-management admin panel for residential complexes: houses and their
sections/floors, apartments and owners, service tariffs, personal accounts and
staff roles with granular permissions.

Built with Django 5 + PostgreSQL, with Celery/Redis handling transactional email
out of the request cycle.

![CI](https://github.com/ValeriaTsentylo/MyHouse24/actions/workflows/ci.yml/badge.svg)

## Screenshots

<!-- Додай 2-3 скріншоти у docs/screenshots/ і розкоментуй.
     Це найважливіша частина README для рекрутера. -->
<!-- ![Houses](docs/screenshots/houses.png) -->
<!-- ![Apartments](docs/screenshots/apartments.png) -->

## Stack

| Layer      | Choice                                             |
| ---------- | -------------------------------------------------- |
| Backend    | Django 5.1, Python 3.12                            |
| Database   | PostgreSQL 16                                      |
| Async      | Celery 5 + Redis                                   |
| Auth       | django-allauth (email-based, mandatory verification) |
| Frontend   | Django templates + AdminLTE, django-ajax-datatable |
| Tooling    | Poetry, Task, ruff, pytest, pre-commit, Docker     |

## Features

- Custom `User` model with email login and 19 granular permissions, grouped into
  roles and enforced through `StaffRequiredMixin`
- Houses with nested sections, floors and assigned staff, edited through inline
  formsets in a single atomic transaction
- Apartments with owners, tariffs and server-side filtered datatables
- Services, units of measurement, tariffs and per-tariff service pricing
- Personal accounts for residents
- Async transactional email through Celery, dispatched on transaction commit
- reCAPTCHA-protected signup

### Roadmap

- Payments section: receipts, incoming/outgoing statements (models done, UI pending)
- Statistics dashboard
- Master-application (service request) workflow

## Data model

![Database schema](docs/DB_schema.png)

## Quick start

```bash
cp .env.example .env_local        # заповни SECRET_KEY та решту
docker compose up --build
```

The app is served on <http://localhost:8000>. Create an admin account with:

```bash
docker compose exec web python manage.py createsuperuser
```

### Local development without Docker

Requires Python 3.12, PostgreSQL and Redis running locally.

```bash
poetry install --with dev
cp .env.example .env_local
task migrate
task runserver
task celery                       # в окремому терміналі
```

## Tests

```bash
task test                         # pytest --cov=src
```

`tests/test_access_control.py` walks the live URLConf and asserts that every
non-public view rejects anonymous requests, so newly added views are covered
without touching the test.

## Project layout

```
config/           settings, URLs, Celery app
src/
  core/           shared models (gallery) and access-control mixins
  users/          custom user model, auth flows, staff CRUD
  roles/          roles and permission mapping
  houses/         houses, sections, floors, staff assignment
  apartments/     apartments and owners
  service/        services, units, tariffs, personal accounts
  payments_section/  receipts and statements
  statistic/      dashboards
tests/            pytest suite
```

## License

MIT
EOF

c_ok "README.md переписано"
commit "docs: rewrite README

Explains what the project is, the stack and the reasoning behind it, how to
run it in one command, what is implemented versus planned, and where the
tests live. Moves the ER diagram into docs/ and references it."

# ─────────────────────────────────────────────────────────────
# Підсумок
# ─────────────────────────────────────────────────────────────
c_step "Готово"

echo
git --no-pager log --oneline "$(git merge-base HEAD main 2>/dev/null || echo HEAD~9)"..HEAD 2>/dev/null || git --no-pager log --oneline -10
echo
printf 'Гілка: \033[1m%s\033[0m\n' "$BRANCH"
printf 'Попереджень: %s\n' "$WARNINGS"
cat <<'NEXT'

Далі вручну:

  1. poetry lock --no-update && poetry install --with dev
     (у pyproject додались dev-залежності — lock треба оновити)
  2. task test
     Частина тестів на доступ може впасти — це і є список в'юх,
     де міксин не проліз. Дивись git diff і дороби вручну.
  3. poetry run pre-commit install && poetry run pre-commit run --all-files
     Перший прогін перепише форматування — це нормально, зроби окремий коміт.
  4. git diff main --stat  — переглянь усе перед пушем.
  5. Додай 2-3 скріншоти в docs/screenshots/ і розкоментуй їх у README.
     Для репо в резюме це дає більше, ніж будь-який рефакторинг.

Що НЕ автоматизовано (потребує твого рішення):
  * User.about_me = TextField() без blank=True — обов'язкове поле для всіх
    користувачів. Виправлення потребує нової міграції.
  * У залежностях одночасно psycopg2-binary і psycopg — лишити треба один.
  * customize_row() у дататейблах генерує HTML рядками в Python —
    варто винести в шаблон через render_to_string.
  * config/settings.py одним файлом — напрошується settings/{base,local,prod}.py.
  * src/roles/views.py і src/roles/views/ існують одночасно.
NEXT
