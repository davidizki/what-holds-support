# What Holds website and support

Public product, support, and privacy pages for the What Holds iPhone, iPad, and Mac app.

- Product: <https://davidizki.github.io/what-holds-support/>
- Support: <https://davidizki.github.io/what-holds-support/support.html>
- Privacy: <https://davidizki.github.io/what-holds-support/privacy.html>

## Deployment

GitHub Pages publishes the repository root from `main` with HTTPS enforcement. The product, support, privacy, and error pages are static HTML and CSS with no JavaScript, advertising, or analytics. One unlisted, `noindex` acceptance fixture uses a short inline script to prove that What Holds can acquire a public article whose text appears only after client-side rendering; it sends no analytics or user data.

## Local verification

The repository does not use a custom GitHub Actions test workflow. Install the
tracked Git pre-push hook once per clone:

```sh
./scripts/install_local_checks.sh
```

The hook runs the structural checker locally and stops the push if it fails.
You can also run it directly:

```sh
python3 scripts/check_site.py
```

For a rendered check, serve the repository and inspect compact and desktop widths:

```sh
python3 -m http.server 8765
```

Then open <http://localhost:8765/> and verify Product, Support, Privacy, keyboard focus, light/dark appearance, and horizontal overflow.

GitHub Pages publishes the site from `main`. GitHub records its required Pages
deployment as an Actions run, but this repository is public, so standard-runner
minutes are free and do not consume the private-account Actions allowance.
