# 🧁 Contributor Pie Chart Generator

This GitHub Action generates a pie chart showing the contribution of each author in your repository, based on commit counts.

## Usage

Add the following to your `.github/workflows/contributor-chart.yml`:

```yaml
name: Generate Contributor Pie Chart

on:
  push:
    branches:
      - main  # Trigger on push to the main branch

jobs:
  generate:
    uses: your-username/contrib-pie-generator/.github/workflows/main.yml@v1
    with:
      chart-size: '8,8'  # Optional input for chart size


```
![Contributor Pie](contributor-pie.png)
