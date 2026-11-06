# Gold Coast Auto Group website

Static marketing site for Gold Coast Auto Group (Great Neck, NY). Four pages, no build step.

| File | Page |
| --- | --- |
| `index.html` | Home |
| `services.html` | Services (`#sourcing`, `#financing`, `#delivery`, `#exotic`) |
| `about.html` | About Jared |
| `contact.html` | Quote form (`?intent=sourcing|financing|delivery|exotic` prefills it) |

Shared pieces: `css/site.css` (all styling, design tokens at the top), `js/site.js` (mobile menu + quote form), `images/` (WebP + JPEG fallbacks at 1600 px and 900 px).

## Editing

- Text: open the HTML file and change the words. The header and footer are repeated in each file, so a change there is made four times.
- Phone number: search for `5165183592` and `(516) 518-3592`.
- Colors and fonts: the `:root` block at the top of `css/site.css`.

## Quote form

Submissions are sent by [Web3Forms](https://web3forms.com). Create a free access key for the destination email and paste it into `FORM_ACCESS_KEY` in `js/site.js`. Until a key is set the form runs in preview mode: it shows the thank-you message but sends nothing.

## Things still waiting on assets

- Jared's headshot: replace the `JH` placeholder block in `about.html` with an `<img>` (comment in the file shows where).
- Instagram, Facebook and Google reviews links: the footer "Follow" column and the "See our Google reviews" link are marked `hidden`; set the `href` and remove `hidden`.
- Social preview image: `images/og.jpg` (1200 x 630) is referenced in each page's `og:image` tag but not yet created.
- Canonical URLs assume `goldcoastautogroup.com`; change if the domain differs.

## Local preview

Open `index.html` in a browser, or run `python3 -m http.server` in this folder and visit http://localhost:8000.
