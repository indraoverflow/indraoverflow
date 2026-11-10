The GitHub image proxy caches by URL, not by file content. After editing
`banner-dark.svg` or `banner-light.svg`, bump the `?v=` suffix on all three
references in the root `README.md`, otherwise the profile keeps serving the
previous image for hours.

The banner is an identity band, not the hero: the name, title and summary are
HTML in the README so they stay legible on a phone, where the column is about
308 px wide.
