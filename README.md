# What Holds website and support

Public product, support, and privacy pages for the What Holds iPhone, iPad, and Mac app.

`brand-mark.svg` is the website copy of the app repository's vector master at `Resources/Brand/WhatHoldsMark.svg`. `app-icon.png` is rasterised from that same master for browser and social surfaces. Change the vector geometry once, then update both repositories in the same release so the shipping icon, in-app navigation, website header, and browser icon remain one identity.

- Product: <https://davidizki.github.io/what-holds-support/>
- Support: <https://davidizki.github.io/what-holds-support/support.html>
- Privacy: <https://davidizki.github.io/what-holds-support/privacy.html>

## Deployment

GitHub Pages publishes the repository root from `main` with HTTPS enforcement. The product, support, privacy, and error pages use semantic static HTML, one shared stylesheet, and a small dependency-free interaction script. The script provides progressive enhancement for reveal motion, six evidence-labelled learning-science panels, the product demos, and keyboard-accessible tabs; it sends no analytics or user data. One unlisted, `noindex` acceptance fixture uses a short inline script to prove that What Holds can acquire a public article whose text appears only after client-side rendering.

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

Then open <http://localhost:8765/> and verify Product, Support, Privacy, every science/product tab, keyboard focus, sticky navigation, desktop and compact layouts, and horizontal overflow.

GitHub Pages publishes the site from `main`. GitHub records its required Pages
deployment as an Actions run, but this repository is public, so standard-runner
minutes are free and do not consume the private-account Actions allowance.
