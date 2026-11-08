# Gold Coast Auto Group website

One-page marketing site for Gold Coast Auto Group (Great Neck, NY). No build step: upload the folder to any web host and it works.

| File | What it is |
| --- | --- |
| `index.html` | The whole site: hero, intro, four steps, Jared, reviews, quote form, footer |
| `css/site.css` | All styling. Colors and fonts are the variables at the top. |
| `js/site.js` | The quote form (and the only JavaScript on the page) |
| `images/` | Two photos as WebP with JPEG fallbacks |

## Editing

- Text: open `index.html` and change the words.
- Phone number: search for `5165183592` and `(516) 518-3592`.
- Colors and fonts: the `:root` block at the top of `css/site.css`.

## Quote form

Submissions are sent by [Web3Forms](https://web3forms.com). Create a free access key for the email that should receive requests and paste it into `FORM_ACCESS_KEY` in `js/site.js`. Until a key is set the form runs in preview mode: it shows the thank-you message but sends nothing.

## Still waiting on

- Jared's headshot: replace the `JH` block in `index.html` with an `<img>` (there is a comment showing where).
- A social preview image at `images/og.jpg` (1200 x 630), referenced in the page head.
- The domain. Canonical and sitemap URLs assume `goldcoastautogroup.com`.

## Local preview

Double-click `index.html`, or run `python3 -m http.server` in this folder and open http://localhost:8000.
