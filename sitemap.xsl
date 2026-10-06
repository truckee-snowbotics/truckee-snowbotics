<?xml version="1.0" encoding="UTF-8"?>
<!-- Styles sitemap.xml for people opening it in a browser. Search engines ignore this. -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sm="http://www.sitemaps.org/schemas/sitemap/0.9">
  <xsl:output method="html" encoding="UTF-8" indent="yes" />

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="robots" content="noindex" />
        <title>Sitemap · Truckee Snowbotics</title>
        <link rel="icon" type="image/svg+xml" href="/images/site/favicon.svg" />
        <link rel="stylesheet" href="/assets/css/main.css" />
        <style>
          .sitemap-list { border-top: 1px solid var(--border); }
          .sitemap-row {
            display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 1.5rem; align-items: baseline;
            padding: 1.1rem 0; border-bottom: 1px solid var(--border);
          }
          .sitemap-name { font-size: 1.05rem; font-weight: 600; color: var(--heading); }
          .sitemap-name:hover { color: var(--accent); }
          .sitemap-url { display: block; margin-top: .15rem; font-size: .85rem; color: var(--text-dim); word-break: break-all; }
          .sitemap-date { font-size: .85rem; color: var(--text-dim); white-space: nowrap; }
        </style>
      </head>
      <body>
        <header class="site-header">
          <div class="header-inner">
            <a href="/" class="header-brand">
              <img src="/images/site/logo.svg" alt="" width="30" height="30" />
              <span>Truckee Snowbotics</span>
            </a>
          </div>
        </header>
        <main>
          <section class="page-hero">
            <h1>Sitemap</h1>
            <p>Every page on snowbotics.org (<xsl:value-of select="count(sm:urlset/sm:url)" /> pages).</p>
          </section>
          <section class="section">
            <div class="section-inner">
              <div class="sitemap-list">
                <xsl:for-each select="sm:urlset/sm:url">
                  <xsl:variable name="path" select="substring-after(substring-after(sm:loc, '://'), '/')" />
                  <div class="sitemap-row">
                    <div>
                      <a class="sitemap-name" href="{sm:loc}">
                        <xsl:choose>
                          <xsl:when test="$path = ''">Home</xsl:when>
                          <xsl:otherwise>
                            <xsl:value-of select="translate(substring($path, 1, 1), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
                            <xsl:value-of select="substring(translate($path, '/', ''), 2)" />
                          </xsl:otherwise>
                        </xsl:choose>
                      </a>
                      <span class="sitemap-url"><xsl:value-of select="sm:loc" /></span>
                    </div>
                    <span class="sitemap-date">Updated <xsl:value-of select="sm:lastmod" /></span>
                  </div>
                </xsl:for-each>
              </div>
            </div>
          </section>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
