# SPMO holdings treemap

Downloads Invesco's SPMO holdings CSV export, writes `spmo.txt`, and fetches the latest available **regular-hours one-minute bar** for every equity symbol with yfinance (falling back to daily bars when needed). It writes an interactive, searchable `spmo.html` treemap. Rectangle area uses Invesco's percentage weight, green/red compares Yahoo's latest bar with the prior trading session's final bar, and missing quotes appear gray with `N/A`. The source date and quote time are displayed in the chart.

## Use locally

Requires Python 3.12 (3.11 should also work).

```bash
python -m pip install -r requirements.txt
python generate_spmo.py
```

To process a saved Invesco export without downloading it again:

```bash
python generate_spmo.py --source /path/to/SPMO_holdings.csv
```

Open `spmo.html` in a browser. D3.js loads from jsDelivr, so the browser needs internet access. The text file is tab separated: `symbol`, `company`, and `weight_pct` (percentage points). Each published ticker is kept, including separate share classes. Dot or slash tickers become Yahoo's dash form. No weight scaling is applied. Common stocks, REITs, and ADRs are included; cash and money-market rows are excluded.

Quotes come from yfinance one-minute regular-hours bars and, for tickers without intraday data, daily closing bars. The page shows the timestamp of the latest bar (Pacific time) or the date of a daily fallback. Requests run in batches of 10, pause two seconds between batches, and back off for 30 then 60 seconds when a batch returns nothing. Use `--quote-batch-size`, `--quote-delay`, and `--quote-retry-delay` to tune that pacing. If Yahoo does not return a quote for a few stocks, their tiles remain visible as `N/A`. If a full batch keeps failing or more than 10% of quotes fail, generation stops and leaves the previous outputs in place. Yahoo may still rate limit shared runners; rerun the workflow later if that happens.

## Publish on GitHub

1. Make a new GitHub repository with `main` as its default branch. Copy **all** project files and folders to its root and push them, including `.github/workflows/update-spmo.yml` and `treemap_template.html`.
2. Under **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
3. Under **Settings → Actions → General**, allow workflows and grant **Read and write permissions** to `GITHUB_TOKEN` if your repository policy requires it. The workflow itself requests `contents: write`, `pages: write`, and `id-token: write`.
4. Open **Actions → Refresh SPMO holdings map → Run workflow** for the first run. Successful runs commit `spmo.txt` and `spmo.html` and deploy the chart directly to Pages. The site URL appears in **Settings → Pages** and in the workflow's deployment job. For a normal project repository it is `https://YOUR_USERNAME.github.io/YOUR_REPO/spmo.html` (the root URL also opens the chart).

The workflow runs daily at **6:35 AM America/Los_Angeles**, with daylight saving handled by GitHub. Runs can be delayed by GitHub's scheduler. A job will fail before committing or publishing if the download, parsing, or most quote lookups fail. Invesco's source data can lag the market on weekends and holidays.

The included starter `spmo.html` and `spmo.txt` contain a September 24, 2026 snapshot obtained from ETFIQ's freely reusable book, whose source field points to Invesco's issuer feed. Prices are marked `N/A`. The first successful workflow run replaces both with the latest holdings from Invesco's CSV and current Yahoo prices.

Sources: [Invesco SPMO holdings page](https://www.invesco.com/us/financial-products/etfs/holdings?audienceType=Investor&ticker=SPMO), [Invesco CSV export](https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Investor&action=download&ticker=SPMO), [ETFIQ open-data terms](https://etfiq.com/data/), [GitHub schedule syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule), [Pages publishing setup](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
