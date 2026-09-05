`slugify("Café del Mar")` returns `"café-del-mar"` — the accented letter is still
in there. I want accented Latin letters folded down to plain ASCII first, so it
returns `"cafe-del-mar"`. Letters that have no ASCII equivalent should just be
dropped, as they are now.

Can you fix that?
