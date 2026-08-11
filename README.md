# What Holds website and support

Public product, support, and privacy pages for the What Holds iPhone, iPad, and Mac app.

- Product: <https://davidizki.github.io/what-holds-support/>
- Support: <https://davidizki.github.io/what-holds-support/support.html>
- Privacy: <https://davidizki.github.io/what-holds-support/privacy.html>

## Deployment

GitHub Pages publishes the repository root from `main` with HTTPS enforcement. The site is static HTML and CSS with no JavaScript, advertising, or analytics.

## Local verification

Run the structural checker:

```sh
python3 scripts/check_site.py
```

For a rendered check, serve the repository and inspect compact and desktop widths:

```sh
python3 -m http.server 8765
```

Then open <http://localhost:8765/> and verify Product, Support, Privacy, keyboard focus, light/dark appearance, and horizontal overflow.
