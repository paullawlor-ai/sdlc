# Release Checklist

1. Update `VERSION` and `CHANGELOG.md`.
2. Regenerate adapters with `python scripts/generate_adapters.py`.
3. Run `python -m unittest discover -s tests -v` on Windows and Linux.
4. Run `python scripts/generate_adapters.py --check`.
5. Run `python scripts/sdlc.py check` and review the token report.
6. Exercise fresh and upgrade installations for each assistant selection.
7. Confirm every starter project installs and passes its smoke tests in CI.
8. Confirm migration guidance for the previous supported release.
9. Confirm the repository owner has selected an appropriate redistribution
   licence before publishing public packages or release archives.
10. Tag the release with the exact version from `VERSION`.
