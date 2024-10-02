name: Update Hausing Scraper

on:
  schedule:
    - cron: '0 * * * *'  # Run hourly
  workflow_dispatch:  # Allow manual triggering
  push:
    branches:
      - main  # Trigger on pushes to the main branch

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout scraper repo
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12.6'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4

    - name: Run scraper script
      run: |
        python src/scraper.py

    - name: Checkout GitHub Pages repo
      uses: actions/checkout@v4
      with:
        repository: celestegambardella/celestegambardella.github.io
        ref: dev  # Checkout the dev branch
        path: src/  # This checks out the GitHub Pages repo to the "src" directory

    - name: Copy markdown to GitHub Pages repo
      run: |
        cp src/output/hausing-scraper.md src/content/work/hausing-scrapper.md

    - name: Commit changes to dev branch
      run: |
        cd work
        git checkout dev
        current_time=$(date +"%Y-%m-%d %H:%M:%S")
        git add src/content/work/hausing-scrapper.md
        git commit -m "Update Hausing Scraper results at $current_time"
        git push origin dev
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    # Step to create a pull request from dev to prod
    - name: Create Pull Request from dev to prod
      uses: peter-evans/create-pull-request@v5
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        base: prod  # Target branch to merge into
        head: dev  # Source branch to merge from
        title: 'Automated Update from dev to prod'
        body: 'This is an automated pull request to merge changes from dev to prod.'

    # Optionally merge the pull request automatically if you want
    - name: Merge PR to prod branch
      uses: actions/github-script@v7
      with:
        script: |
          const { data: pullRequests } = await github.pulls.list({
            owner: context.repo.owner,
            repo: context.repo.repo,
            state: 'open',
            head: 'dev',
          });

          if (pullRequests.length > 0) {
            await github.pulls.merge({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pullRequests[0].number,
            });
          }
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
