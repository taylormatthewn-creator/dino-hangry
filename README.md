# Dino Hangry Rocks — Phaser Edition

This is the 8-bit Nintendo-style version of the dinosaur rock-smashing game.

It is no longer a Streamlit app. It is now a real browser game using **Phaser**, an HTML5 game framework.

## What changed

- The T-Rex walks around a forest map.
- The player uses arrow keys or WASD.
- The T-Rex smashes rocks by walking into them or pressing Space/Enter next to them.
- Food is hidden under rocks.
- Cavemen chase and attack the dinosaur.
- A genie creates extra rocks.
- The ninja helper unlocks at Level 6.
- Every 10th level is a boss level.
- Between levels, there is a timed crystal puzzle mini-game.
- The first version includes 50 levels.

## Controls

Keyboard:

- Arrow keys or WASD: move the T-Rex
- Space or Enter: stomp/attack next to the T-Rex

Touchscreen or mouse:

- Use the on-screen controller buttons in the lower-right corner of the game.

## How Phaser is linked

Phaser is loaded in `index.html` with this script tag:

```html
<script src="https://cdn.jsdelivr.net/npm/phaser@3.90.0/dist/phaser.min.js"></script>
```

Then the game code is loaded after Phaser:

```html
<script src="game.js"></script>
```

That order matters. Phaser must load before `game.js`.

## How to put this on GitHub Pages

1. Create a new GitHub repository, or reuse the existing game repository.
2. Upload these files to the root of the repo:
   - `index.html`
   - `game.js`
   - `README.md`
3. Commit the files.
4. Go to the repo on GitHub.
5. Click **Settings**.
6. Click **Pages** in the left menu.
7. Under **Build and deployment**, choose:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/root**
8. Click **Save**.
9. Wait a minute or two. GitHub will give you a public game link.

The link usually looks like:

```text
https://YOUR-GITHUB-NAME.github.io/YOUR-REPO-NAME/
```

## How to test locally

Because Phaser games run in the browser, it is best to use a local web server instead of just double-clicking `index.html`.

Easy Python option:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Optional later upgrades

Good next steps:

- Add custom pixel art sprites instead of simple generated pixel sprites.
- Add walking animations.
- Add sound effects and music.
- Add a larger scrolling world.
- Add save slots with `localStorage`.
- Add more puzzle-room types.
- Add story dialogue for the ninja, genie, and cavemen boss.
