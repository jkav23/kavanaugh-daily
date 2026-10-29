# The Kavanaugh Daily — starter website

A personal, mobile-friendly news homepage for Cape Breton, Nova Scotia, Canada, the world, business, technology, health, and selected sports.

## Preview without installing anything

Open `index.html` in a desktop browser. It includes a **dated starter edition** for preview purposes. Weather requires an internet connection. Some browsers restrict reading separate `news.json` files over `file://`, so the page includes a built-in starter edition.

For a local server test:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Publish free through GitHub Pages

1. Create a GitHub account if necessary, and create a new **public** repository called `kavanaugh-daily`. GitHub Pages on GitHub Free requires public repositories.
2. Upload the contents of this folder to the repository, keeping the `.github/workflows/publish.yml` file and `scripts/update_news.py` in the same structure. If uploading in the GitHub web interface, ensure hidden dot-folders are included (or upload files individually).
3. Open the repository **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Open **Actions → Update and publish The Kavanaugh Daily → Run workflow** to trigger the first headline update and deployment. Allow necessary workflow permissions if GitHub prompts.
5. Once the job has completed, use the URL shown in **Settings → Pages**. The site should be at `https://YOUR-USERNAME.github.io/kavanaugh-daily/` (replace username).
6. On your iPhone open it in Safari, choose **Share → Add to Home Screen**.

The included GitHub Actions workflow attempts morning and afternoon updates (with backup attempts at **5:17 and 6:41 a.m.**, and **2:13 and 3:29 p.m.**, `America/Halifax` local time), subject to GitHub Actions queue delays and provider availability. GitHub can disable scheduled workflows after 60 days of inactivity in public repositories; check occasionally.

## What currently works

- Responsive homepage and sections, keyword search, favourites, topic preference settings stored in your browser.
- A generated MP3 audio news briefing with a neural narrator, plus a text transcript.
- Live current weather and a short forecast for New Waterford via Open-Meteo, requiring an online connection.
- News retrieval from Google News RSS with dates, titles, sources, and links (which may route through Google News), including dedicated **Technology** coverage of AI, devices, cybersecurity, Canadian technology, and software.

## Planned, not implemented yet

- A full 10-minute professionally scripted audio bulletin (the present audio is a shorter recorded headline roundup).
- Automated relevance scoring and feedback-learning system across devices.
- Photographs, licensed thumbnails, full-article summaries, scores integration, dedicated archives.

## Limitations and attribution

RSS headline collection is best-effort and may fail if Google News changes its feeds or rate-limits requests. No licensed article images are copied. The site republishes headline metadata and links; it does not scrape full articles. RSS snippets are intentionally not republished. Story headlines can be misleading; read the original report for verification. The starter edition is dated October 2026, and its seed timestamps are approximate where a source did not disclose a precise time. Weather is powered by [Open-Meteo](https://open-meteo.com/) (CC BY 4.0). This project is intended for personal/non-commercial use.