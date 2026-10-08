# Working on this site (for AI agents)

1. **Pushing is publishing.** This repository is public, and a push makes changes live on
   https://bartlettcj.github.io. Commit freely; push only when the owner has said, in the current
   conversation, to push this site.
2. **Identity.** Commits must be authored as `Chris Bartlett <317579833+BartlettCJ@users.noreply.github.com>`.
   This is set in the repository's own git config; check with `git config user.email` before
   committing. The machine's global identity is a different, private account and must never appear
   in this history.
3. **Remote.** `origin` is `git@github-bartlettcj:BartlettCJ/BartlettCJ.github.io.git`. The
   `github-bartlettcj` host alias (in the owner's `~/.ssh/config`) routes this one account through
   its own SSH key, so the HTTPS sign-in other repositories use is never asked to choose an account.
   Test it with `ssh -T git@github-bartlettcj`: it should greet BartlettCJ.
4. **Build.** Edit `build.py` (the content lists near the top), run
   `python C:\BartlettCJ.github.io\_build\build.py`, then preview with
   `python -m http.server 8772 --directory C:\BartlettCJ.github.io` and look at the pages.
5. **Stable PDF names.** Never rename a hosted PDF when a new version comes out; replace its bytes.
   Google Scholar remembers the address.
6. **Text.** The home page introduction is the owner's own wording; change it only on his say-so.
   Facts about the papers come from the records, never from memory.
7. **Local settings.** `_build/local_settings.json` exists only on the owner's computer and is never
   committed. If it is missing, the build still works and leaves out what it supplies.
8. **Keep `google4b557c5777779b29.html`** in the site root. It proves ownership to Google Search
   Console; deleting it loses the verification.
