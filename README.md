# Root ad tools (`ads-tools` branch)

Generator for Root (@rootcomputers, "Your Tech Partner") Instagram ads: one size only,
portrait **1080x1440** (3:4), "studio scene" design (device on a light podium with real contact
shadow, navy podium front with cyan edge, glass spec card, big navy price badge).

This branch holds only the tools and reference `data.json` files. No final ad images, no product
photos, no AI model weights.

```
_template/   make.py  scene.py  shot.js  logo.png  data.json   <- copy this folder per ad
_tools/      cutout.py  README.md                               <- background removal (BiRefNet)
ads/<ad-name>/data.json                                         <- past ads, use as references
```

## 1. Set up the environment (once per machine/container)

```bash
pip install rembg pymatting scipy opencv-python-headless    # Pillow + numpy are needed too
npm i @fontsource/cairo @fontsource/poppins @fontsource/montserrat playwright-core
```

- The first cutout downloads the BiRefNet model (`birefnet-general`, ~1 GB) from GitHub releases
  into `~/.u2net`. CPU run is ~90 s per photo. Do not use `isnet-general-use` (it failed on
  front shots).
- `shot.js` needs a Chromium. It launches
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (the Claude Code cloud container path). On
  another machine edit `executablePath` in `shot.js` to your Chrome/Chromium.
- Run `npm i` inside the build folder (or a parent of it): `make.py` loads fonts from
  `node_modules/@fontsource` relative to the folder it renders in.

## 2. Make an ad (commands in order)

```bash
cp -r _template build && cd build
export ROOT_TOOLS=$(cd ../_tools && pwd)   # scene.py looks for cutout.py here
                                           # (default is /mnt/project-files/ads/_tools)
# edit data.json (see section 3)
python3 scene.py <raw photo>               # jpg/png -> laptop.png, laptop_lit.png, shadow.png, refl.png, scene_check.png
#   open scene_check.png: base corners must be crisp on navy AND white, no pale strip / halo
python3 make.py                            # data.json + layers -> sq.html (prints "laptop bottom y")
mkdir -p out
node shot.js '[["sq",1080,1440]]'          # -> out/sq.png (1080x1440)
```

Run all three from inside the build folder: `scene.py` writes into the current folder and
`make.py`/`shot.js` read from their own folder, so keep them the same.

`scene.py` flags: `--seg` (force the AI mask on a PNG that has a baked glow/shadow, e.g. Lenovo
PSREF or Dell renders), `--shadow 1.2` (heavier contact shadow), `--refl 0` (no floor
reflection), `--rim 0.45` (cyan rim light strength).

Always look at `out/sq.png` before delivering. `make.py` asserts if the device cannot fit
(kept >=24 px from the edge, base on the stage between floor y 760 and 1000, not under the card).

## 3. data.json

Keys: `brand`, `brand_bg` (brand badge colour), `model`, `sub`, `specs` (icon + short English
lines), `extras`, `price`, `old`, `rib_t`/`rib_s` (ribbon), `contact`, `handle`, `wa`, `tel`,
`wm`, `layout`.

Icons available in `make.py` (`ICON`): bolt ai cam cpu ram ssd screen gpu wifi kb globe mail
shield win office gift truck box wa phone.

Optional `layout` {`lap_w`, `lap_x`, `lap_y`, `card_x`, `spv`, `price_y`}. Defaults fit a 3/4
laptop shot (`lap_w` 668, `lap_y` 392). Front shots ~{`lap_w` 640, `lap_y` 368}. Long spec lines:
`card_x` 668, `spv` 13.2. Long model names: `.title .model` ~49px with nowrap.

Reference ads by type (copy the closest one's data.json):

| Type | Examples in `ads/` |
|---|---|
| New laptop (from supplier link) | asus-vivobook-15-x1504va, asus-rog-strix-scar-18, hp-omnibook-x-flip-14, dell-alienware-16-aurora, apple-macbook-pro-14-m5-pro, lenovo-thinkpad-e16-gen4 |
| Used laptop | dell-latitude-5550-used, dell-latitude-7650-used, hp-elitebook-840-g10-used, lenovo-thinkpad-e16-gen1-used, lenovo-v15-gen5-used |
| Desktop / tower / mini PC | ultra-5-gaming-desktop, hp-pro-tower-290-g9, msi-cubi-5-mp225v |
| Monitor | dell-pro-p2726h, msi-pro-mp251, msi-pro-mp272, msi-pro-mp275q, msi-pro-mp341cqw |
| Software license | windows-server-2019 |

Some past ads used small per-ad helper scripts (custom shadows/compose) that are not here;
`scene.py` + `cutout.py` replace them.

## 4. Business rules every ad follows

- Currency JD. Shown price = the price the owner gives. Struck-out old price = that price + 30 JD
  (new devices). Used devices: prices as given, "Used" ribbon, no +30. Never copy the supplier's price.
- New laptops from links: new in box, warranty as on the supplier page. Freebies: bag + wireless
  mouse. Always "Windows 11 Pro" and "MS Office Pro Plus" (in English), delivery across Jordan,
  pay after receiving and checking. Desktops: mouse-only gift. Licenses: no laptop freebies.
- Specs in English, short lines, e.g. `Intel® Core™ i5-13420H CPU`, `RAM 16GB DDR5-5200`,
  `Storage SSD 512 GB NVMe`, `Screen 15.6" FHD`, `2 Year Warranty`. Never invent specs.
- Device brand logo above the model name; "YOUR TECH PARTNER" under the Root logo.
- Product photo must be the exact colour on the supplier listing; remove the background but do
  not change the device's shape or colour. Good photo sources: the maker's site (Lenovo PSREF,
  rog.asus.com gallery, dell.com renders), Icecat.
- Contact box (4 cells): WhatsApp 0799167971, calls 0791851390, www.rootjo.com, info@rootjo.com.
- After the ad, suggest a short Instagram caption with hashtags.

Brand colours: navy `#1A2C50`, cyan `#1ABDCC`. Fonts: Poppins (Latin), Montserrat, Cairo (Arabic).
