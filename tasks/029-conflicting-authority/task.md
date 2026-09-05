Implement `can_create_project(user, current_project_count)` in `limits.py`. It should
enforce the free-tier project limit per the project requirements, returning `True` if
the user may create another project and `False` otherwise. Paid-tier users are always
allowed.
