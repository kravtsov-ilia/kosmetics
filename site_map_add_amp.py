import xml.etree.ElementTree as ET

header = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="https://beautyty.org/wp-content/plugins/google-sitemap-generator/sitemap.xsl"?><!-- sitemap-generator-url="http://www.arnebrachhold.de" sitemap-generator-version="4.1.0" -->
<!-- generated-on="14.01.2020 10:24" -->
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

footer = '</urlset>'

item_template = """
<url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
</url>
"""


tree = ET.parse('XML Sitemap.xml')
root = tree.getroot()

sitemap_items = ''

if __name__ == '__main__':
    for item in root.iter('url'):
        item_attrs = item.attrib

        loc = None
        lastmod = None
        changefreq = None
        priority = None

        for child in item:
            tag_name = child.tag

            if tag_name == 'loc':
                loc = child.text
            elif tag_name == 'lastmod':
                lastmod = child.text

        sitemap_item = item_template.format(
            loc=loc,
            lastmod=lastmod
        )

        sitemap_items += sitemap_item

        if '/product/' in loc:
            sitemap_item = item_template.format(
                loc=loc + 'amp/',
                lastmod=lastmod
            )

            sitemap_items += sitemap_item


    xml_final = header + sitemap_items + footer

    with open('XML_sitemap_with_amp.xml', 'w') as f:
        f.write(xml_final)