# webpage-layout

Crawl a site and cluster the pages based on layout.

This has three part

1. Crawling
2. Parsing and feature extraction
3. Clustering based on similarity score.


### Crawling

Open Source Solution :
- Apache Nutch
- Scrapy

- Simple crawler using BeautifulSoup or Selenium webdriver.


### Parsing and Feature Extraction

- Parse the HTML and generate DOM tree
- Parse CSS and generate set of css classes

### Clustering based on similarity score

- Tree edit distance to find similarity for DOM tree
- Cosine / Jacard similarity for css classes
- Cluster pages based on the similarity score.
