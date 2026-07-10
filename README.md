# Dino Hangry Rocks — Phaser 2.5D Forest Adventure

This is the 2.5D Phaser version of the Dino Hangry Rocks game.

It is meant to feel less like a board game and more like an immersive kid-friendly forest adventure. The camera follows the T-Rex through a large jungle path. Rocks, trees, enemies, shadows, particles, and sound-style feedback are all handled inside Phaser.

## How to play

- Move: **Arrow keys** or **WASD**
- Stomp / attack: **Space** or **Enter**
- Roar: **R**
- Touchscreen buttons also appear on screen
- Smash rocks to find food
- Avoid cavemen arrows and attacks
- The genie can spawn extra rocks
- Ninja helper unlocks at Level 6
- Boss levels happen every 10 levels
- The dinosaur must not run out of HP

## Files

- `index.html` — webpage that loads Phaser and the game
- `game.js` — the full game code
- `README.md` — instructions

## How Phaser is linked

The project links to Phaser inside `index.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/phaser@3.90.0/dist/phaser.min.js"></script>
<script src="game.js"></script>
```

The order matters:

1. Phaser loads first.
2. Your game code loads second.

## How to test locally

Because Phaser games are web games, they work best from a local web server.

If you have Python installed, open a terminal in this folder and run:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

You can also upload the files directly to GitHub and use GitHub Pages.

## How to publish with GitHub Pages

1. Upload these files to your GitHub repository:
   - `index.html`
   - `game.js`
   - `README.md`
2. Open the repo on GitHub.
3. Go to **Settings**.
4. Go to **Pages**.
5. Under **Build and deployment**, choose **Deploy from a branch**.
6. Choose branch `main` and folder `/root`.
7. Save.
8. Wait a minute or two for GitHub to publish the site.

GitHub will give you a link like:

```text
https://your-github-name.github.io/your-repo-name/
```

## Design direction

This version uses a 2.5D forest style:

- Angled jungle path
- Big trees and foreground foliage
- Camera follow
- Layered environment
- Larger rocks that feel like objects, not board tiles
- T-Rex shown from behind/above instead of as a flat board piece

If this still does not feel right, the next recommended direction is a side-scrolling jungle platform/adventure version.
