/*
Dino Hangry Rocks — Phaser 2.5D Forest Adventure
No asset files are required. The game creates its own simple sprites/textures with Phaser graphics.
*/

const W = 960;
const H = 540;
const WORLD_W = 2600;
const WORLD_H = 1800;

const SAVE_KEY = "dino_hangry_25d_save_v1";

function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
function dist(a, b) { return Phaser.Math.Distance.Between(a.x, a.y, b.x, b.y); }

class BootScene extends Phaser.Scene {
  constructor() { super("Boot"); }
  preload() {}
  create() {
    makeTextures(this);
    this.scene.start("Title");
  }
}

class TitleScene extends Phaser.Scene {
  constructor() { super("Title"); }
  create() {
    this.cameras.main.setBackgroundColor("#082114");
    drawTitleBackground(this);
    this.add.text(W/2, 72, "DINO HANGRY ROCKS", {
      fontFamily: "Georgia, serif", fontSize: 48, color: "#ffe36f", stroke: "#3a1f08", strokeThickness: 8
    }).setOrigin(0.5);
    this.add.text(W/2, 126, "2.5D FOREST ADVENTURE", {
      fontFamily: "Arial Black, Arial", fontSize: 22, color: "#d8ffe1", stroke: "#06150b", strokeThickness: 4
    }).setOrigin(0.5);

    this.add.image(W/2, 305, "title-card").setScale(1.1);

    const box = this.add.rectangle(W/2, 454, 680, 94, 0x0f2e1d, 0.86).setStrokeStyle(3, 0xffd66b, 0.85);
    this.add.text(W/2, 432, "Move with Arrow Keys or WASD • Stomp with Space/Enter • Roar with R", {
      fontFamily: "Arial", fontSize: 20, color: "#fff8d9"
    }).setOrigin(0.5);
    this.add.text(W/2, 472, "Click or press SPACE to start", {
      fontFamily: "Arial Black, Arial", fontSize: 26, color: "#7dff8d", stroke: "#08200e", strokeThickness: 5
    }).setOrigin(0.5);

    this.input.keyboard.once("keydown-SPACE", () => this.scene.start("Game", { level: 1 }));
    this.input.once("pointerdown", () => this.scene.start("Game", { level: 1 }));
  }
}

class GameScene extends Phaser.Scene {
  constructor() { super("Game"); }

  init(data) {
    this.level = data.level || 1;
  }

  create() {
    this.gameOver = false;
    this.won = false;
    this.lastActionTime = 0;
    this.logs = [];
    this.foodFound = 0;
    this.foodNeeded = Math.min(2 + Math.floor(this.level / 5), 6);
    this.movesLeft = Math.max(72 - Math.floor(this.level * 0.6), 42);
    this.dinoMaxHp = 38 + Math.floor(this.level * 1.6);
    this.dinoHp = this.dinoMaxHp;
    this.ninjaUnlocked = this.level >= 6;
    this.bossLevel = this.level % 10 === 0;
    this.rockHp = 3 + Math.floor(this.level / 4);
    this.genieTimer = 0;

    this.physics.world.setBounds(0, 0, WORLD_W, WORLD_H);
    this.cameras.main.setBounds(0, 0, WORLD_W, WORLD_H);
    this.cameras.main.setZoom(1);

    this.createWorld();
    this.createPlayer();
    this.createObjects();
    this.createHUD();
    this.createControls();

    this.cameras.main.startFollow(this.player.container, true, 0.08, 0.08);
    this.cameras.main.setDeadzone(120, 80);

    this.keys = this.input.keyboard.addKeys("UP,DOWN,LEFT,RIGHT,W,A,S,D,SPACE,ENTER,R");

    this.log("🧞 The genie hid food under rocks in the jungle.");
    if (this.ninjaUnlocked) this.log("🥷 The ninja helper is hiding in the trees and will strike nearby enemies!");
    if (this.bossLevel) this.log("👑 Boss level! Find and defeat the mighty hunter.");
  }

  createWorld() {
    this.bg = this.add.container(0, 0);

    // Deep jungle background bands
    const g = this.add.graphics();
    g.fillGradientStyle(0x0a321c, 0x0a321c, 0x195f35, 0x0b2514, 1);
    g.fillRect(0, 0, WORLD_W, WORLD_H);
    this.bg.add(g);

    // Winding path made of overlapping ellipses
    this.pathGraphics = this.add.graphics();
    this.pathGraphics.fillStyle(0xa66a2f, 1);
    const pathPoints = [];
    for (let y = -100; y < WORLD_H + 200; y += 88) {
      const x = WORLD_W/2 + Math.sin(y / 210) * 340 + Math.sin(y / 95) * 85;
      pathPoints.push({ x, y });
      this.pathGraphics.fillEllipse(x, y, 760 - y * 0.11, 210);
    }
    this.pathGraphics.fillStyle(0xca8b43, 0.46);
    for (const p of pathPoints) this.pathGraphics.fillEllipse(p.x, p.y, 500, 92);

    // grass texture dots, flowers, leaf clusters
    const deco = this.add.graphics();
    for (let i = 0; i < 950; i++) {
      const x = Phaser.Math.Between(0, WORLD_W);
      const y = Phaser.Math.Between(0, WORLD_H);
      const nearPath = Math.abs(x - (WORLD_W/2 + Math.sin(y/210)*340 + Math.sin(y/95)*85)) < 420;
      if (nearPath && Math.random() < 0.55) continue;
      const colors = [0x0f5a2a, 0x17793d, 0x23894b, 0x0b3d22, 0x65b644, 0xf05c3d, 0x7e55ff, 0xffc247];
      deco.fillStyle(colors[Phaser.Math.Between(0, colors.length-1)], Phaser.Math.FloatBetween(0.45, 0.95));
      deco.fillEllipse(x, y, Phaser.Math.Between(5, 18), Phaser.Math.Between(3, 10));
    }
    this.bg.add([this.pathGraphics, deco]);

    // Distant scenery
    for (let i = 0; i < 16; i++) {
      const mountain = this.add.triangle(Phaser.Math.Between(0, WORLD_W), Phaser.Math.Between(40, 500), 0, 150, 130, 0, 260, 150, 0x2d7348, 0.35);
      mountain.setDepth(-20);
    }

    this.sortables = [];
    this.obstacles = [];

    // Large trees and foreground border foliage
    for (let i = 0; i < 120; i++) {
      const y = Phaser.Math.Between(0, WORLD_H);
      let x;
      const pathX = WORLD_W/2 + Math.sin(y/210)*340 + Math.sin(y/95)*85;
      if (Math.random() < 0.5) x = Phaser.Math.Between(0, Math.max(60, pathX - 430));
      else x = Phaser.Math.Between(Math.min(WORLD_W - 60, pathX + 430), WORLD_W);
      this.spawnTree(x, y, Phaser.Math.FloatBetween(0.8, 1.45));
    }

    // Foreground canopy shadows
    const shade = this.add.graphics();
    shade.fillStyle(0x001008, 0.2);
    shade.fillRect(0, 0, WORLD_W, WORLD_H);
    for (let i = 0; i < 50; i++) {
      shade.fillStyle(0x000000, 0.10);
      shade.fillEllipse(Phaser.Math.Between(0, WORLD_W), Phaser.Math.Between(0, WORLD_H), Phaser.Math.Between(160, 340), Phaser.Math.Between(60, 180));
    }
  }

  spawnTree(x, y, scale=1) {
    const trunk = this.add.image(x, y, "tree").setScale(scale);
    trunk.setDepth(y - 40);
    this.sortables.push(trunk);
    this.obstacles.push({ x, y: y + 20, radius: 54 * scale });
    // canopy layer above player adds immersive occlusion
    const canopy = this.add.image(x, y - 86 * scale, "canopy").setScale(scale * 1.18).setAlpha(0.94);
    canopy.setDepth(y + 210);
    this.sortables.push(canopy);
  }

  createPlayer() {
    const start = this.getPathPoint(WORLD_H - 180);
    const shadow = this.add.ellipse(0, 30, 74, 24, 0x000000, 0.32);
    const body = this.add.image(0, 0, "dino-back").setScale(1.05);
    const label = this.add.text(0, 70, "T-REX", { fontFamily: "Arial Black", fontSize: 12, color: "#fff3bb", stroke: "#10200d", strokeThickness: 3 }).setOrigin(0.5);
    const container = this.add.container(start.x, start.y, [shadow, body, label]);
    this.physics.add.existing(container);
    container.body.setCircle(25, -25, -8);
    container.body.setCollideWorldBounds(true);
    container.setDepth(start.y + 50);
    this.player = { container, body, speed: 210, facing: new Phaser.Math.Vector2(0, -1), stomping: false, invuln: 0 };
  }

  createObjects() {
    this.rocks = this.physics.add.group();
    this.foods = this.physics.add.group();
    this.enemies = this.physics.add.group();
    this.projectiles = this.physics.add.group();
    this.effects = this.add.group();

    const rockCount = Math.min(4 + Math.floor(this.level * 0.45), 18);
    const foodIndexes = new Set();
    while (foodIndexes.size < this.foodNeeded) foodIndexes.add(Phaser.Math.Between(0, rockCount - 1));

    for (let i = 0; i < rockCount; i++) {
      const p = this.getPathPoint(Phaser.Math.Between(140, WORLD_H - 260));
      const offset = Phaser.Math.Between(-260, 260);
      const rock = this.spawnRock(p.x + offset, p.y + Phaser.Math.Between(-40, 50));
      rock.setData("hasFood", foodIndexes.has(i));
    }

    const enemyCount = this.bossLevel ? 4 + Math.floor(this.level / 10) : Math.min(1 + Math.floor(this.level / 4), 9);
    for (let i = 0; i < enemyCount; i++) {
      const p = this.getPathPoint(Phaser.Math.Between(120, WORLD_H - 760));
      this.spawnEnemy(p.x + Phaser.Math.Between(-220, 220), p.y + Phaser.Math.Between(-90, 90), false);
    }
    if (this.bossLevel) {
      const p = this.getPathPoint(180);
      this.spawnEnemy(p.x, p.y, true);
    }

    const gp = this.getPathPoint(Phaser.Math.Between(160, 580));
    this.genie = this.add.image(gp.x + 320, gp.y, "genie").setScale(1.05);
    this.physics.add.existing(this.genie, true);
    this.genie.setDepth(gp.y + 20);

    if (this.ninjaUnlocked) {
      const np = this.getPathPoint(WORLD_H - 360);
      this.ninja = this.add.image(np.x - 150, np.y, "ninja").setScale(0.9).setAlpha(0.9);
      this.physics.add.existing(this.ninja);
      this.ninja.body.setCircle(18);
    }
  }

  spawnRock(x, y) {
    const rock = this.rocks.create(x, y, "rock-full");
    rock.setScale(Phaser.Math.FloatBetween(0.9, 1.25));
    rock.body.setCircle(30, 0, 8);
    rock.setData("hp", this.rockHp);
    rock.setData("maxHp", this.rockHp);
    rock.setData("type", "rock");
    rock.setDepth(y + 35);
    rock.body.setImmovable(true);
    return rock;
  }

  spawnEnemy(x, y, boss=false) {
    const enemy = this.enemies.create(x, y, boss ? "boss" : "caveman");
    enemy.setScale(boss ? 1.35 : 0.95);
    enemy.body.setCircle(boss ? 30 : 22, boss ? 2 : 5, boss ? 18 : 15);
    enemy.setData("hp", boss ? 38 + this.level * 2 : 8 + Math.floor(this.level * 1.3));
    enemy.setData("maxHp", enemy.getData("hp"));
    enemy.setData("boss", boss);
    enemy.setData("cooldown", Phaser.Math.Between(500, 1600));
    enemy.setDepth(y + 45);
    return enemy;
  }

  getPathPoint(y) {
    return { x: WORLD_W/2 + Math.sin(y/210)*340 + Math.sin(y/95)*85, y };
  }

  createHUD() {
    this.hud = this.add.container(0, 0).setScrollFactor(0).setDepth(100000);
    const top = this.add.rectangle(W/2, 36, W - 26, 62, 0x0b2114, 0.75).setStrokeStyle(2, 0xf2d078, 0.65);
    this.hud.add(top);
    this.hudText = this.add.text(24, 16, "", { fontFamily: "Arial Black, Arial", fontSize: 18, color: "#fff8d0", stroke: "#000000", strokeThickness: 4 });
    this.hud.add(this.hudText);
    this.missionText = this.add.text(W/2, 16, "", { fontFamily: "Arial Black, Arial", fontSize: 18, color: "#8dff9c", stroke: "#000", strokeThickness: 4 }).setOrigin(0.5, 0);
    this.hud.add(this.missionText);

    this.logBox = this.add.container(14, H - 124).setScrollFactor(0).setDepth(100001);
    this.logBg = this.add.rectangle(0, 0, 430, 104, 0x102f1e, 0.82).setOrigin(0).setStrokeStyle(2, 0xffe090, 0.45);
    this.logText = this.add.text(16, 12, "", { fontFamily: "Arial", fontSize: 16, color: "#fff6d0", wordWrap: { width: 395 }, lineSpacing: 4 });
    this.logBox.add([this.logBg, this.logText]);

    this.helpText = this.add.text(W - 22, H - 22, "Move: WASD/Arrows  •  Stomp: Space/Enter  •  Roar: R", {
      fontFamily: "Arial", fontSize: 15, color: "#fff6d0", stroke: "#000", strokeThickness: 3
    }).setOrigin(1).setScrollFactor(0).setDepth(100001);
  }

  createControls() {
    this.touch = { up:false, down:false, left:false, right:false, stomp:false, roar:false };
    const baseX = W - 142;
    const baseY = H - 132;
    const makeBtn = (x, y, label, key) => {
      const c = this.add.container(x, y).setScrollFactor(0).setDepth(100002).setSize(58, 48).setInteractive({ useHandCursor: true });
      const r = this.add.roundedRect ? null : undefined;
      const bg = this.add.rectangle(0, 0, 58, 48, 0xfff1c6, 0.9).setStrokeStyle(3, 0x5c3b10, 0.8);
      const t = this.add.text(0, 0, label, { fontFamily: "Arial Black", fontSize: 21, color: "#1a2c18" }).setOrigin(0.5);
      c.add([bg, t]);
      c.on("pointerdown", () => { this.touch[key] = true; });
      c.on("pointerup", () => { this.touch[key] = false; });
      c.on("pointerout", () => { this.touch[key] = false; });
      return c;
    };
    makeBtn(baseX, baseY - 56, "⬆", "up");
    makeBtn(baseX, baseY + 56, "⬇", "down");
    makeBtn(baseX - 64, baseY, "⬅", "left");
    makeBtn(baseX + 64, baseY, "➡", "right");
    makeBtn(baseX - 190, baseY + 56, "STOMP", "stomp").first.setSize?.(90,48);
    makeBtn(baseX - 190, baseY - 8, "ROAR", "roar");
  }

  update(time, delta) {
    if (this.gameOver) return;

    this.updatePlayer(delta);
    this.updateEnemies(time, delta);
    this.updateProjectiles();
    this.updateNinja(delta);
    this.updateGenie(time);
    this.updateDepths();
    this.updateHUD();
    this.checkWinLoss();
  }

  updatePlayer(delta) {
    const p = this.player.container;
    let vx = 0, vy = 0;
    if (this.keys.LEFT.isDown || this.keys.A.isDown || this.touch.left) vx -= 1;
    if (this.keys.RIGHT.isDown || this.keys.D.isDown || this.touch.right) vx += 1;
    if (this.keys.UP.isDown || this.keys.W.isDown || this.touch.up) vy -= 1;
    if (this.keys.DOWN.isDown || this.keys.S.isDown || this.touch.down) vy += 1;

    const v = new Phaser.Math.Vector2(vx, vy);
    if (v.length() > 0) {
      v.normalize();
      this.player.facing.copy(v);
      p.body.setVelocity(v.x * this.player.speed, v.y * this.player.speed * 0.82);
      p.scaleX = v.x < -0.1 ? -1 : v.x > 0.1 ? 1 : p.scaleX;
      p.angle = Math.sin(this.time.now / 75) * 1.5;
    } else {
      p.body.setVelocity(0, 0);
      p.angle = 0;
    }

    // soft collision with trees and rocks
    for (const obs of this.obstacles) {
      const d = Phaser.Math.Distance.Between(p.x, p.y, obs.x, obs.y);
      if (d < obs.radius + 28) {
        const away = new Phaser.Math.Vector2(p.x - obs.x, p.y - obs.y).normalize();
        p.x += away.x * 3.2;
        p.y += away.y * 2.8;
      }
    }

    const stompPressed = Phaser.Input.Keyboard.JustDown(this.keys.SPACE) || Phaser.Input.Keyboard.JustDown(this.keys.ENTER) || this.touch.stomp;
    const roarPressed = Phaser.Input.Keyboard.JustDown(this.keys.R) || this.touch.roar;
    if (stompPressed && this.time.now - this.lastActionTime > 280) this.stomp();
    if (roarPressed && this.time.now - this.lastActionTime > 500) this.roar();

    if (this.player.invuln > 0) {
      this.player.invuln -= delta;
      p.alpha = this.player.invuln > 0 ? 0.55 + Math.sin(this.time.now / 45) * 0.25 : 1;
    }
  }

  stomp() {
    this.lastActionTime = this.time.now;
    this.movesLeft = Math.max(0, this.movesLeft - 1);
    const p = this.player.container;
    const target = { x: p.x + this.player.facing.x * 54, y: p.y + this.player.facing.y * 46 };
    this.cameras.main.shake(70, 0.005);
    this.spawnDust(target.x, target.y);

    let hitSomething = false;

    this.rocks.children.each(rock => {
      if (!rock.active) return;
      if (Phaser.Math.Distance.Between(target.x, target.y, rock.x, rock.y) < 85) {
        hitSomething = true;
        let hp = rock.getData("hp") - (2 + Math.floor(this.level / 9));
        rock.setData("hp", hp);
        rock.setTint(0xfff0a0);
        this.time.delayedCall(90, () => rock.clearTint());
        rock.setTexture(hp <= rock.getData("maxHp") / 2 ? "rock-cracked" : "rock-full");
        this.log("🦖 STOMP! The rock cracks.");
        if (hp <= 0) this.breakRock(rock);
      }
    });

    this.enemies.children.each(enemy => {
      if (!enemy.active) return;
      if (Phaser.Math.Distance.Between(target.x, target.y, enemy.x, enemy.y) < 86) {
        hitSomething = true;
        this.damageEnemy(enemy, 6 + Math.floor(this.level / 4), "🦖 The T-Rex chomps and stomps!");
      }
    });

    if (!hitSomething) this.log("🦖 The T-Rex stomps the ground. Boom!");
  }

  roar() {
    this.lastActionTime = this.time.now;
    this.movesLeft = Math.max(0, this.movesLeft - 1);
    const p = this.player.container;
    const ring = this.add.circle(p.x, p.y, 30, 0xfff06d, 0.2).setDepth(p.y + 200);
    this.tweens.add({ targets: ring, radius: 180, alpha: 0, duration: 420, onComplete: () => ring.destroy() });
    let scared = 0;
    this.enemies.children.each(enemy => {
      if (!enemy.active) return;
      if (dist(p, enemy) < 250) {
        scared++;
        const away = new Phaser.Math.Vector2(enemy.x - p.x, enemy.y - p.y).normalize();
        enemy.x += away.x * 60;
        enemy.y += away.y * 45;
        enemy.setData("cooldown", enemy.getData("cooldown") + 800);
      }
    });
    this.log(scared ? `🦖 ROAR! ${scared} enemy${scared > 1 ? "ies" : ""} backed away.` : "🦖 ROAR! The jungle echoes.");
  }

  breakRock(rock) {
    const x = rock.x, y = rock.y;
    this.spawnDust(x, y);
    if (rock.getData("hasFood")) {
      const food = this.foods.create(x, y, "food");
      food.setDepth(y + 60);
      food.body.setCircle(16);
      this.log("🍖 Food popped out from under the rock!");
    } else if (Math.random() < 0.14) {
      const gem = this.add.image(x, y, "crystal").setDepth(y + 70).setScale(0.7);
      this.tweens.add({ targets: gem, y: y - 20, alpha: 0, duration: 1200, onComplete: () => gem.destroy() });
      this.log("💎 Crystal sparkle! Bonus XP!");
    } else {
      this.log("🪨 The rock shattered into pebbles.");
    }
    rock.destroy();
  }

  updateEnemies(time, delta) {
    const p = this.player.container;
    this.enemies.children.each(enemy => {
      if (!enemy.active) return;
      const d = dist(p, enemy);
      const speed = enemy.getData("boss") ? 76 : 88 + this.level * 1.2;
      if (d < 450) {
        const dir = new Phaser.Math.Vector2(p.x - enemy.x, p.y - enemy.y).normalize();
        enemy.body.setVelocity(dir.x * speed, dir.y * speed * 0.82);
        enemy.scaleX = dir.x < 0 ? -Math.abs(enemy.scaleX) : Math.abs(enemy.scaleX);
      } else enemy.body.setVelocity(0, 0);

      enemy.setData("cooldown", enemy.getData("cooldown") - delta);
      if (d < 58 && enemy.getData("cooldown") <= 0) {
        this.hurtDino(enemy.getData("boss") ? 7 : 3, enemy.getData("boss") ? "👑 The boss hunter hits hard!" : "🧔 Caveman bonk!");
        enemy.setData("cooldown", enemy.getData("boss") ? 1200 : 1500);
      } else if (d < 360 && enemy.getData("cooldown") <= 0 && Math.random() < 0.8) {
        this.throwArrow(enemy, p);
        enemy.setData("cooldown", enemy.getData("boss") ? 1000 : 1800);
      }
    });

    this.physics.overlap(this.player.container, this.foods, (_, food) => {
      food.destroy();
      this.foodFound++;
      this.dinoHp = Math.min(this.dinoMaxHp, this.dinoHp + 5);
      this.log("🍖 Chomp! Food calms the T-Rex's hangry-ness.");
    });
  }

  throwArrow(enemy, target) {
    const arrow = this.projectiles.create(enemy.x, enemy.y, "arrow");
    const v = new Phaser.Math.Vector2(target.x - enemy.x, target.y - enemy.y).normalize();
    arrow.body.setVelocity(v.x * 260, v.y * 260);
    arrow.rotation = Math.atan2(v.y, v.x);
    arrow.setData("life", 1500);
    arrow.setDepth(enemy.y + 100);
  }

  updateProjectiles() {
    this.projectiles.children.each(arrow => {
      if (!arrow.active) return;
      arrow.setData("life", arrow.getData("life") - 16);
      if (arrow.getData("life") <= 0) arrow.destroy();
      if (dist(this.player.container, arrow) < 34) {
        arrow.destroy();
        this.hurtDino(3 + Math.floor(this.level / 8), "🏹 A caveman arrow hits the T-Rex!");
      }
    });
  }

  updateNinja(delta) {
    if (!this.ninja) return;
    const p = this.player.container;
    const toPlayer = new Phaser.Math.Vector2(p.x - 75 - this.ninja.x, p.y + 30 - this.ninja.y);
    if (toPlayer.length() > 4) {
      toPlayer.normalize();
      this.ninja.body.setVelocity(toPlayer.x * 160, toPlayer.y * 130);
    } else this.ninja.body.setVelocity(0, 0);
    this.ninja.setDepth(this.ninja.y + 55);

    this.enemies.children.each(enemy => {
      if (!enemy.active) return;
      if (dist(this.ninja, enemy) < 62 && Math.random() < 0.018) {
        this.damageEnemy(enemy, 3, "🥷 Ninja strike!");
        this.ninja.setTint(0xffffff);
        this.time.delayedCall(90, () => this.ninja.clearTint());
      }
    });
  }

  updateGenie(time) {
    this.genieTimer += 16;
    const threshold = Math.max(6200 - this.level * 55, 3600);
    if (this.genieTimer > threshold) {
      this.genieTimer = 0;
      if (this.rocks.countActive(true) < 22) {
        const p = this.getPathPoint(Phaser.Math.Between(120, WORLD_H - 220));
        const r = this.spawnRock(p.x + Phaser.Math.Between(-260, 260), p.y);
        r.setData("hasFood", Math.random() < 0.18);
        this.log("🧞 Genie trick! A new rock blocks the path.");
      }
    }
  }

  damageEnemy(enemy, amount, message) {
    enemy.setData("hp", enemy.getData("hp") - amount);
    enemy.setTint(0xffe16b);
    this.time.delayedCall(80, () => enemy.clearTint());
    this.spawnDust(enemy.x, enemy.y);
    this.log(message);
    if (enemy.getData("hp") <= 0) {
      this.log(enemy.getData("boss") ? "👑 Boss defeated!" : "🧔 Caveman ran away!");
      enemy.destroy();
    }
  }

  hurtDino(amount, message) {
    if (this.player.invuln > 0) return;
    this.dinoHp = Math.max(0, this.dinoHp - amount);
    this.player.invuln = 800;
    this.cameras.main.shake(110, 0.009);
    this.log(message);
  }

  spawnDust(x, y) {
    for (let i = 0; i < 10; i++) {
      const d = this.add.image(x, y, "dust").setScale(Phaser.Math.FloatBetween(0.35, 0.85)).setDepth(y + 120).setAlpha(0.75);
      this.tweens.add({
        targets: d,
        x: x + Phaser.Math.Between(-42, 42),
        y: y + Phaser.Math.Between(-28, 26),
        alpha: 0,
        scale: 0.08,
        duration: Phaser.Math.Between(280, 520),
        onComplete: () => d.destroy()
      });
    }
  }

  updateDepths() {
    this.player.container.setDepth(this.player.container.y + 60);
    this.rocks.children.each(o => o.setDepth(o.y + 40));
    this.enemies.children.each(o => o.setDepth(o.y + 50));
    this.foods.children.each(o => o.setDepth(o.y + 60));
    if (this.genie) this.genie.setDepth(this.genie.y + 40);
  }

  updateHUD() {
    this.hudText.setText(`🦖 HP ${this.dinoHp}/${this.dinoMaxHp}   🍖 ${this.foodFound}/${this.foodNeeded}   👣 ${this.movesLeft}   LVL ${this.level}/50   🥷 ${this.ninjaUnlocked ? "Helper" : "Locked"}`);
    this.missionText.setText(this.bossLevel ? "BOSS LEVEL: defeat the hunter and find food!" : "Explore the jungle, stomp rocks, and find food!");
    this.logText.setText(this.logs.slice(-4).join("\n"));
  }

  log(msg) {
    this.logs.push(msg);
    if (this.logs.length > 10) this.logs.shift();
  }

  checkWinLoss() {
    if (this.dinoHp <= 0 || this.movesLeft <= 0) {
      this.endLevel(false);
      return;
    }
    const noBossLeft = !this.bossLevel || this.enemies.children.entries.every(e => !e.active || !e.getData("boss"));
    if (this.foodFound >= this.foodNeeded && noBossLeft) this.endLevel(true);
  }

  endLevel(won) {
    this.gameOver = true;
    this.physics.pause();
    const overlay = this.add.rectangle(W/2, H/2, W, H, 0x041008, 0.76).setScrollFactor(0).setDepth(200000);
    const title = won ? "LEVEL COMPLETE!" : "TRY AGAIN!";
    const color = won ? "#9cff8f" : "#ff9275";
    this.add.text(W/2, H/2 - 80, title, {
      fontFamily: "Arial Black, Arial", fontSize: 46, color, stroke: "#000", strokeThickness: 7
    }).setOrigin(0.5).setScrollFactor(0).setDepth(200001);
    const line = won ? "The T-Rex found enough food and survived the jungle." : "The T-Rex got too tired or too hurt.";
    this.add.text(W/2, H/2 - 16, line, { fontFamily: "Arial", fontSize: 22, color: "#fff5d5", stroke: "#000", strokeThickness: 4 }).setOrigin(0.5).setScrollFactor(0).setDepth(200001);
    const next = won && this.level < 50 ? "Press SPACE for crystal puzzle, then next level" : "Press SPACE to restart";
    this.add.text(W/2, H/2 + 52, next, { fontFamily: "Arial Black", fontSize: 22, color: "#ffe36f", stroke: "#000", strokeThickness: 5 }).setOrigin(0.5).setScrollFactor(0).setDepth(200001);
    this.input.keyboard.once("keydown-SPACE", () => {
      if (won && this.level < 50) this.scene.start("Crystal", { level: this.level + 1 });
      else this.scene.start("Game", { level: won ? 1 : this.level });
    });
    this.input.once("pointerdown", () => {
      if (won && this.level < 50) this.scene.start("Crystal", { level: this.level + 1 });
      else this.scene.start("Game", { level: won ? 1 : this.level });
    });
  }
}

class CrystalScene extends Phaser.Scene {
  constructor() { super("Crystal"); }
  init(data) { this.nextLevel = data.level || 2; }
  create() {
    this.cameras.main.setBackgroundColor("#09192f");
    for (let i = 0; i < 80; i++) {
      this.add.circle(Phaser.Math.Between(0, W), Phaser.Math.Between(0, H), Phaser.Math.Between(1, 3), 0x88d5ff, Phaser.Math.FloatBetween(0.2, 0.8));
    }
    this.add.text(W/2, 64, "CRYSTAL PUZZLE", { fontFamily: "Arial Black", fontSize: 44, color: "#c99cff", stroke: "#000", strokeThickness: 7 }).setOrigin(0.5);
    this.add.text(W/2, 112, "Drag the glowing crystal pieces into the circle before time runs out!", { fontFamily: "Arial", fontSize: 20, color: "#fff6d0" }).setOrigin(0.5);
    this.timer = 14;
    this.timerText = this.add.text(W/2, 158, "", { fontFamily: "Arial Black", fontSize: 24, color: "#ffe36f", stroke: "#000", strokeThickness: 5 }).setOrigin(0.5);
    this.target = this.add.circle(W/2, 314, 88, 0x7e42ff, 0.18).setStrokeStyle(4, 0xcaa7ff, 0.95);
    this.add.image(W/2, 314, "crystal-outline").setScale(1.5).setAlpha(0.35);
    this.pieces = [];
    const starts = [[190,260],[250,410],[710,240],[760,410]];
    for (let i = 0; i < 4; i++) {
      const piece = this.add.image(starts[i][0], starts[i][1], `crystal-piece-${i}`).setScale(1.25).setInteractive({ draggable: true, useHandCursor: true });
      piece.setData("placed", false);
      this.pieces.push(piece);
    }
    this.input.on("drag", (pointer, obj, x, y) => { obj.x = x; obj.y = y; });
    this.input.on("dragend", (pointer, obj) => {
      if (Phaser.Math.Distance.Between(obj.x, obj.y, W/2, 314) < 110) {
        obj.setData("placed", true);
        obj.x = W/2 + Phaser.Math.Between(-28, 28);
        obj.y = 314 + Phaser.Math.Between(-28, 28);
        obj.disableInteractive();
        obj.setAlpha(0.92);
      }
    });
    this.time.addEvent({ delay: 1000, loop: true, callback: () => this.timer-- });
  }
  update() {
    this.timerText.setText(`Time: ${this.timer}`);
    if (this.pieces.every(p => p.getData("placed"))) this.finish(true);
    if (this.timer <= 0) this.finish(false);
  }
  finish(success) {
    if (this.done) return;
    this.done = true;
    this.add.rectangle(W/2, H/2, W, H, 0x000000, 0.62).setDepth(10);
    this.add.text(W/2, H/2 - 20, success ? "CRYSTAL RESTORED!" : "TIME'S UP — KEEP GOING!", { fontFamily: "Arial Black", fontSize: 36, color: success ? "#9cffef" : "#ffd36f", stroke: "#000", strokeThickness: 7 }).setOrigin(0.5).setDepth(11);
    this.add.text(W/2, H/2 + 40, "Press SPACE for the next forest level", { fontFamily: "Arial", fontSize: 22, color: "#fff6d0", stroke: "#000", strokeThickness: 4 }).setOrigin(0.5).setDepth(11);
    this.input.keyboard.once("keydown-SPACE", () => this.scene.start("Game", { level: this.nextLevel }));
    this.input.once("pointerdown", () => this.scene.start("Game", { level: this.nextLevel }));
  }
}

function makeTextures(scene) {
  const g = scene.add.graphics();

  // Dino from behind
  g.clear();
  g.fillStyle(0x000000, 0.22); g.fillEllipse(70, 118, 86, 24);
  g.fillStyle(0x3b8f2f, 1); g.fillEllipse(70, 72, 58, 82);
  g.fillStyle(0x2f7f2a, 1); g.fillEllipse(70, 43, 48, 42);
  g.fillStyle(0x2b6d24, 1); g.fillTriangle(40, 83, 6, 124, 62, 104);
  g.fillStyle(0x67b947, 1); g.fillEllipse(56, 109, 18, 28); g.fillEllipse(85, 109, 18, 28);
  g.fillStyle(0xffa13a, 1); for (let y=30; y<100; y+=13) g.fillTriangle(70,y,64,y+10,76,y+10);
  g.fillStyle(0xf2fff2, 1); g.fillEllipse(53, 122, 12, 7); g.fillEllipse(87, 122, 12, 7);
  g.generateTexture("dino-back", 140, 135);

  // Tree
  g.clear();
  g.fillStyle(0x000000, 0.28); g.fillEllipse(65, 145, 88, 24);
  g.fillStyle(0x6a3a18, 1); g.fillRoundedRect(42, 38, 48, 115, 18);
  g.fillStyle(0x8a5221, 1); g.fillRoundedRect(57, 40, 12, 110, 8);
  g.fillStyle(0x0f4723, 1); g.fillEllipse(65, 36, 118, 80);
  g.fillStyle(0x166b34, 1); g.fillEllipse(36, 64, 80, 60); g.fillEllipse(96, 64, 84, 60);
  g.fillStyle(0x248245, 1); g.fillEllipse(65, 24, 72, 48);
  g.generateTexture("tree", 130, 165);

  g.clear();
  g.fillStyle(0x083516, 0.96); g.fillEllipse(80, 80, 150, 100);
  g.fillStyle(0x0f632c, 0.95); g.fillEllipse(44, 92, 98, 78); g.fillEllipse(112, 92, 105, 78);
  g.fillStyle(0x1a8642, 0.95); g.fillEllipse(80, 53, 94, 64);
  g.generateTexture("canopy", 160, 150);

  // Rocks
  function rockTexture(name, cracked=false) {
    g.clear();
    g.fillStyle(0x000000, 0.26); g.fillEllipse(55, 76, 88, 20);
    g.fillStyle(0x8b8c86, 1); g.fillEllipse(55, 50, 82, 62);
    g.fillStyle(0xb8b8ae, 1); g.fillEllipse(39, 36, 38, 30); g.fillEllipse(65, 34, 42, 36);
    g.fillStyle(0x5f625c, 1); g.fillEllipse(76, 56, 35, 28);
    g.fillStyle(0x6faa4c, 1); g.fillEllipse(46, 30, 18, 8); g.fillEllipse(74, 41, 20, 8);
    if (cracked) { g.lineStyle(4, 0x343434, 1); g.beginPath(); g.moveTo(55,20); g.lineTo(48,43); g.lineTo(62,52); g.lineTo(54,72); g.strokePath(); }
    g.generateTexture(name, 110, 92);
  }
  rockTexture("rock-full", false); rockTexture("rock-cracked", true);

  // Caveman and boss
  g.clear();
  g.fillStyle(0x000000, 0.25); g.fillEllipse(45, 73, 58, 14);
  g.fillStyle(0xbf7a41, 1); g.fillCircle(45, 31, 21);
  g.fillStyle(0x55351d, 1); g.fillEllipse(45, 18, 44, 18);
  g.fillStyle(0x8b5428, 1); g.fillTriangle(24, 52, 66, 52, 45, 82);
  g.lineStyle(5, 0x55351d, 1); g.lineBetween(18, 48, 3, 35); g.lineBetween(70, 48, 88, 35);
  g.fillStyle(0xffffff, 1); g.fillCircle(37, 31, 3); g.fillCircle(53, 31, 3);
  g.generateTexture("caveman", 95, 90);

  g.clear();
  g.fillStyle(0x000000, 0.28); g.fillEllipse(60, 96, 86, 22);
  g.fillStyle(0x7d3f1b, 1); g.fillCircle(60, 34, 28);
  g.fillStyle(0x2b180b, 1); g.fillEllipse(60, 17, 70, 22);
  g.fillStyle(0x65330e, 1); g.fillRoundedRect(33, 55, 56, 52, 12);
  g.fillStyle(0xffd45e, 1); g.fillTriangle(31, 12, 43, 1, 49, 20); g.fillTriangle(89, 12, 77, 1, 71, 20);
  g.lineStyle(7, 0x2b180b, 1); g.lineBetween(20,60,3,40); g.lineBetween(98,60,119,40);
  g.generateTexture("boss", 125, 118);

  // genie, ninja, food, arrow, dust, crystals
  g.clear();
  g.fillStyle(0x54d7ff, 1); g.fillCircle(38, 30, 20); g.fillStyle(0x2d73ff, 1); g.fillEllipse(38, 58, 42, 45); g.fillStyle(0xffdf68,1); g.fillRoundedRect(16, 13, 44, 8, 4); g.generateTexture("genie", 80, 90);
  g.clear();
  g.fillStyle(0x1a102f,1); g.fillCircle(32, 29, 19); g.fillRoundedRect(18,44,30,38,10); g.fillStyle(0xb18cff,1); g.fillRect(20,24,24,6); g.generateTexture("ninja", 70, 88);
  g.clear();
  g.fillStyle(0xb36420,1); g.fillEllipse(40,40,40,28); g.fillStyle(0xf5d0a5,1); g.fillCircle(65,45,11); g.fillCircle(73,48,8); g.generateTexture("food", 90, 80);
  g.clear();
  g.lineStyle(5, 0xc98733, 1); g.lineBetween(0,10,52,10); g.fillStyle(0xd9d9d9,1); g.fillTriangle(52,10,38,0,38,20); g.generateTexture("arrow", 58, 22);
  g.clear();
  g.fillStyle(0xd6bd7c, 0.9); g.fillCircle(12,12,12); g.generateTexture("dust", 24, 24);
  g.clear();
  g.fillStyle(0x7c4dff,1); g.fillTriangle(30,0,60,30,30,80); g.fillStyle(0x63e8ff,1); g.fillTriangle(30,0,0,30,30,80); g.generateTexture("crystal", 60, 82);
  g.clear();
  g.lineStyle(5, 0xcaa7ff, 1); g.strokeTriangle(50, 0, 100, 55, 50, 130); g.strokeTriangle(50, 0, 0, 55, 50, 130); g.generateTexture("crystal-outline", 105, 135);
  for (let i=0;i<4;i++) {
    g.clear();
    const cols = [0x7c4dff,0x42ddff,0xc053ff,0x8ff8ff];
    g.fillStyle(cols[i],1); g.fillTriangle(40,0,80,50,20,80); g.lineStyle(3,0xffffff,0.5); g.strokeTriangle(40,0,80,50,20,80); g.generateTexture(`crystal-piece-${i}`, 90, 90);
  }

  // title card
  g.clear();
  g.fillGradientStyle(0x0d5b2c,0x0d5b2c,0x7bb84d,0x144124,1); g.fillRoundedRect(0,0,520,210,24);
  g.fillStyle(0x9b5e27,1); g.fillEllipse(260,170,450,60);
  g.fillStyle(0x6a3a18,1); g.fillRoundedRect(35,20,50,150,14); g.fillRoundedRect(430,16,55,154,16);
  g.fillStyle(0x8b8c86,1); g.fillEllipse(310,130,100,70); g.fillEllipse(385,120,96,64); g.fillEllipse(235,125,90,60);
  g.fillStyle(0x3b8f2f,1); g.fillEllipse(180,124,66,88); g.fillStyle(0xffa13a,1); for(let y=75;y<143;y+=14) g.fillTriangle(180,y,173,y+10,187,y+10);
  g.generateTexture("title-card", 520, 210);
  g.destroy();
}

function drawTitleBackground(scene) {
  const g = scene.add.graphics();
  g.fillGradientStyle(0x07180f, 0x07180f, 0x1a7441, 0x082114, 1);
  g.fillRect(0, 0, W, H);
  for (let i=0; i<50; i++) {
    g.fillStyle(Phaser.Math.RND.pick([0x0f5a2a,0x1d8448,0x4fb15c,0x74451c]), Phaser.Math.FloatBetween(0.2,0.85));
    g.fillEllipse(Phaser.Math.Between(0,W), Phaser.Math.Between(0,H), Phaser.Math.Between(40,160), Phaser.Math.Between(16,60));
  }
}

// Small polyfill-style helper for rounded rectangles if the browser build uses older graphics APIs.
Phaser.GameObjects.Graphics.prototype.fillRoundedRect = Phaser.GameObjects.Graphics.prototype.fillRoundedRect || Phaser.GameObjects.Graphics.prototype.fillRect;

const config = {
  type: Phaser.AUTO,
  parent: "game-wrap",
  width: W,
  height: H,
  backgroundColor: "#07180f",
  physics: { default: "arcade", arcade: { debug: false } },
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, TitleScene, GameScene, CrystalScene]
};

new Phaser.Game(config);
