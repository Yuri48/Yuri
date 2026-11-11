# Gold Coast Auto Group website

One-page marketing site for Gold Coast Auto Group (Great Neck, NY). No build step: upload the folder to any web host and it works.

| File | What it is |
| --- | --- |
| `index.html` | The whole site: hero, intro, three steps, Jared, reviews, quote form (with Instagram link), footer |
| `css/site.css` | All styling. Colors and fonts are the variables at the top. |
| `js/site.js` | The quote form (and the only JavaScript on the page) |
| `images/` | Two photos as WebP with JPEG fallbacks |

## Editing

- Text: open `index.html` and change the words.
- Phone number: search for `5165183592` and `(516) 518-3592`.
- Colors and fonts: the `:root` block at the top of `css/site.css`.

## Quote form

Submissions are sent by [Web3Forms](https://web3forms.com) to Jared@goldcoastautogroup.com, using the access key in `FORM_ACCESS_KEY` in `js/site.js`. If the key is removed, the form runs in preview mode: it shows the thank-you message but sends nothing.

## Still waiting on

- A larger headshot. `images/jared.jpg` is 447 px square; 1000 px or more would look sharper.
- A social preview image at `images/og.jpg` (1200 x 630), referenced in the page head.
- The domain. Canonical and sitemap URLs assume `goldcoastautogroup.com`.

## Putting it on IONOS

Upload everything inside this `gold-coast-auto` folder (not the folder itself) to the web space root in IONOS, using the IONOS file manager or SFTP. `index.html` must sit at the top level, next to the `css`, `js` and `images` folders.

## Local preview

Double-click `index.html`, or run `python3 -m http.server` in this folder and open http://localhost:8000.
