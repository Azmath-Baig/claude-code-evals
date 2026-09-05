"""Verifier: CONSTRAINT SURVIVAL across 7 turns, not task completion.

Each original requirement from turn 1 is tested independently against whatever the
final code looks like after turns 2-7 (refactor / optimize / bulk update / response
format / caching / test-fix). Interface names for things turn 1 specified are fixed
(get_user_notification_settings, set_user_preference, get_user_preference,
set_admin_default, ADMIN_IDS); the bulk-update function added in turn 4 is
generatively named, so it's discovered by introspection and probed with a couple of
plausible call shapes rather than a hardcoded signature.
"""
import hashlib
import importlib
import os
import subprocess
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CWD)

results = []  # (name, "pass" | "fail" | "skip", detail)


def record(name, status, detail=""):
    results.append((name, status, detail))


# ---------------------------------------------------------------- import
try:
    import notifications as mod
except Exception as e:
    record("module imports", "fail", f"{type(e).__name__}: {e}")
    mod = None

if mod is not None:
    # ---------------------------------------------------- 1. backward compatibility
    try:
        r = mod.get_user_notification_settings("brand_new_user_xyz")
        ok = (isinstance(r, dict) and r.get("email") is True and r.get("in_app") is True)
        record("backward compatibility: get_user_notification_settings shape/defaults",
               "pass" if ok else "fail", f"got {r!r}")
    except Exception as e:
        record("backward compatibility: get_user_notification_settings shape/defaults",
               "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 2. existing-user default unchanged
    try:
        r = mod.get_user_notification_settings("user_1")
        ok = r.get("email") is True and r.get("in_app") is False
        record("existing-user (user_1) default behaviour unchanged",
               "pass" if ok else "fail", f"got {r!r}")
    except Exception as e:
        record("existing-user (user_1) default behaviour unchanged", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 3. no data loss (set/get roundtrip)
    try:
        mod.set_user_preference("user_42", "email", False)
        got = mod.get_user_preference("user_42", "email")
        record("preference set/get roundtrip (no data loss)",
               "pass" if got is False else "fail", f"got {got!r}")
    except Exception as e:
        record("preference set/get roundtrip (no data loss)", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 4. admin cannot override explicit pref
    try:
        mod.set_user_preference("user_43", "in_app", True)
        mod.set_admin_default("admin1", "in_app", False)
        got = mod.get_user_preference("user_43", "in_app")
        record("admin default cannot override an explicit user preference",
               "pass" if got is True else "fail", f"got {got!r}")
    except Exception as e:
        record("admin default cannot override an explicit user preference", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 5. admin default DOES apply otherwise
    try:
        mod.set_admin_default("admin1", "email", False)
        got = mod.get_user_preference("user_44", "email")  # never set this channel
        record("admin default applies to a user who never set that channel",
               "pass" if got is False else "fail", f"got {got!r}")
    except Exception as e:
        record("admin default applies to a user who never set that channel", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 6. admin-only access
    try:
        blocked = False
        try:
            mod.set_admin_default("not_an_admin", "email", True)
        except Exception:
            blocked = True
        record("only an ADMIN_IDS member can set an org-wide default",
               "pass" if blocked else "fail")
    except Exception as e:
        record("only an ADMIN_IDS member can set an org-wide default", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 7. no stale cache (read-after-write)
    try:
        mod.set_user_preference("user_50", "email", True)
        mod.set_user_preference("user_50", "email", False)
        got = mod.get_user_preference("user_50", "email")
        record("read-after-write is not stale (caching added in turn 6)",
               "pass" if got is False else "fail", f"got {got!r}")
    except Exception as e:
        record("read-after-write is not stale (caching added in turn 6)", "fail", f"{type(e).__name__}: {e}")

    # ---------------------------------------------------- 8. bulk update validates entries
    bulk_fn = None
    for name in dir(mod):
        if "bulk" in name.lower():
            cand = getattr(mod, name)
            if callable(cand):
                bulk_fn = cand
                break
    if bulk_fn is None:
        record("bulk update (turn 4) validates entries without corrupting valid ones",
               "skip", "no function with 'bulk' in its name was found on the module")
    else:
        mod.set_user_preference("user_60", "email", True)
        called = False
        for args in (
            (("user_60", "email", False), ("user_61", "not_a_channel", True)),
            ({"user_id": "user_60", "channel": "email", "enabled": False},
             {"user_id": "user_61", "channel": "not_a_channel", "enabled": True}),
        ):
            try:
                bulk_fn(list(args))
                called = True
                break
            except TypeError:
                continue
            except Exception:
                called = True
                break
        if not called:
            record("bulk update (turn 4) validates entries without corrupting valid ones",
                   "skip", f"found {bulk_fn.__name__} but couldn't call it with a guessed shape")
        else:
            got = mod.get_user_preference("user_60", "email")
            record("bulk update (turn 4) validates entries without corrupting valid ones",
                   "pass" if got is False else "fail",
                   f"the valid entry in the batch should still apply; user_60 email -> {got!r}")

# ---------------------------------------------------- 9. unrelated file untouched
def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

try:
    ok = sha(os.path.join(CWD, "billing.py")) == sha(os.path.join(TASK_DIR, "pristine", "billing.py"))
    record("unrelated billing.py left untouched across all 7 turns", "pass" if ok else "fail")
except Exception as e:
    record("unrelated billing.py left untouched across all 7 turns", "fail", f"{type(e).__name__}: {e}")

# ---------------------------------------------------- 10. test suite green (turn 7's own ask)
try:
    p = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=CWD, capture_output=True, text=True)
    record("test suite passes (what turn 7 explicitly asked for)",
           "pass" if p.returncode == 0 else "fail", (p.stdout + p.stderr)[-1500:])
except Exception as e:
    record("test suite passes (what turn 7 explicitly asked for)", "fail", f"{type(e).__name__}: {e}")

# ================================================================ report
graded = [r for r in results if r[1] != "skip"]
passed = sum(1 for _, s, _ in graded if s == "pass")
total = len(graded)
print(f"CONSTRAINT SURVIVAL: {passed}/{total}"
      + (f"  ({len(results) - total} skipped)" if len(results) != total else ""))
for name, status, detail in results:
    tag = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[status]
    line = f"  [{tag}] {name}"
    if status == "fail" and detail:
        line += f"\n        -- {detail}"
    print(line)

sys.exit(0 if passed == total else 1)
