The `user` table has gotten wide. The address columns (`street`, `city`,
`postal_code`, `country`) really belong in their own place — pull them out of
`user` into a separate table.

Existing code calls `create_user(name, email, street, city, postal_code, country)`
and `get_user(id)` and expects the address values back from `get_user`. Those calls
must keep working unchanged.
