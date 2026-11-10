GitHub's image and raw CDNs cache by URL path for several minutes, and a query
string does not reliably bypass that cache. After changing a banner, give the
file a new name (`banner-dark-v3.svg`) and update the three references in the
root `README.md`; editing the file in place can serve the previous image for a
while.

The banner is an identity band, not the hero. The name, title and summary are
HTML in the README so they stay legible on a phone, where the column is about
308 px wide. SVG is used so the band stays sharp at every width.
