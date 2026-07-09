/*
Dino Hangry Rocks - Phaser Edition
A kid-friendly 8-bit style browser game.

Controls:
- Arrow keys or WASD: move
- Space / Enter: stomp or attack next to the T-Rex
- Click/tap the on-screen buttons on phones/tablets
- On puzzle screens: click crystal pieces before the timer runs out
*/

const TILE = 32;
const MAP_COLS = 20;
const MAP_ROWS = 15;
const GAME_W = TILE * MAP_COLS;
const GAME_H = TILE * MAP_ROWS;
const UI_H = 160;
const WORLD_H = GAME_H + UI_H;

const COLORS = {
  bg: 0x0f2f1f,
  panel: 0x102f24,
  panel2: 0x1f4b36,
  text: '#fff6cc',
  gold: '#ffe26a',
  red: '#ff6b6b',
  blue: '#87d7ff',
  green: '#9fff93'
};

function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
function key(x, y) { return `${x},${y}`; }
function manhattan(a, b) { return Math.abs(a.x - b.x) + Math.abs(a.y - b.y); }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function samePos(a, b) { return a.x === b.x && a.y === b.y; }

class BootScene extends Phaser.Scene {
  constructor() { super('Boot'); }
  preload() {}
  create() {
    this.createPixelTextures();
    this.scene.start('Title');
  }

  createPixelTextures() {
    const g = this.add.graphics();

    const make = (name, draw) => {
      g.clear();
      draw(g);
      g.generateTexture(name, TILE, TILE);
    };

    make('tile_grass1', g => {
      g.fillStyle(0x2f8f49); g.fillRect(0,0,32,32);
      g.fillStyle(0x3fa65a); g.fillRect(2,4,4,12); g.fillRect(20,12,4,8); g.fillRect(10,22,12,3);
      g.fillStyle(0x1f6f3d); g.fillRect(0,30,32,2);
    });
    make('tile_grass2', g => {
      g.fillStyle(0x277f42); g.fillRect(0,0,32,32);
      g.fillStyle(0x4db963); g.fillRect(8,5,6,16); g.fillRect(18,18,8,4); g.fillRect(3,24,7,3);
      g.fillStyle(0x1f6f3d); g.fillRect(0,30,32,2);
    });
    make('tree', g => {
      g.fillStyle(0x216d35); g.fillRect(0,0,32,32);
      g.fillStyle(0x7b4d2a); g.fillRect(13,16,6,14);
      g.fillStyle(0x0d5229); g.fillRect(6,6,20,14); g.fillRect(9,2,14,12); g.fillRect(3,12,26,8);
      g.fillStyle(0x39aa55); g.fillRect(9,5,5,4); g.fillRect(19,12,5,4);
    });
    make('rock', g => {
      g.fillStyle(0x2f8f49); g.fillRect(0,0,32,32);
      g.fillStyle(0x565f65); g.fillRect(6,12,20,13); g.fillRect(10,8,14,7); g.fillRect(4,18,24,6);
      g.fillStyle(0x8a969c); g.fillRect(10,10,8,4); g.fillRect(8,17,6,3);
      g.fillStyle(0x343a40); g.fillRect(20,18,5,3);
    });
    make('hardrock', g => {
      g.fillStyle(0x2f8f49); g.fillRect(0,0,32,32);
      g.fillStyle(0x7d6953); g.fillRect(5,11,22,14); g.fillRect(9,6,15,8); g.fillRect(3,18,26,7);
      g.fillStyle(0xb18b66); g.fillRect(10,8,8,4); g.fillRect(7,16,6,3);
      g.fillStyle(0x4a372c); g.fillRect(20,18,5,3);
    });
    make('food', g => {
      g.fillStyle(0x2f8f49); g.fillRect(0,0,32,32);
      g.fillStyle(0xffe0b0); g.fillRect(8,12,16,8); g.fillStyle(0xe84a3a); g.fillRect(11,9,10,10); g.fillRect(13,7,6,4);
      g.fillStyle(0xffffff); g.fillRect(5,14,5,4); g.fillRect(22,14,5,4);
    });
    make('dino', g => {
      g.fillStyle(0x00a85a); g.fillRect(6,13,17,10); g.fillRect(18,9,9,8); g.fillRect(4,20,8,5);
      g.fillStyle(0x23d17a); g.fillRect(8,11,10,5); g.fillRect(20,8,5,3);
      g.fillStyle(0xffffff); g.fillRect(24,11,2,2);
      g.fillStyle(0x102010); g.fillRect(25,11,1,1);
      g.fillStyle(0x007241); g.fillRect(9,23,4,6); g.fillRect(19,22,4,7); g.fillRect(2,17,5,3);
      g.fillStyle(0xfff0c0); g.fillRect(25,15,4,1); g.fillRect(25,17,3,1);
    });
    make('ninja', g => {
      g.fillStyle(0x23283a); g.fillRect(10,8,12,16); g.fillRect(8,13,16,10);
      g.fillStyle(0xd4f1ff); g.fillRect(12,12,8,3);
      g.fillStyle(0xffdb82); g.fillRect(14,13,2,2); g.fillRect(18,13,2,2);
      g.fillStyle(0xbdd9ff); g.fillRect(23,8,3,18);
    });
    make('caveman', g => {
      g.fillStyle(0x9a6131); g.fillRect(9,9,14,14); g.fillStyle(0x6b3f22); g.fillRect(7,6,18,8); g.fillRect(6,10,5,5); g.fillRect(21,10,5,5);
      g.fillStyle(0xffc18a); g.fillRect(11,11,10,7); g.fillStyle(0x222222); g.fillRect(13,13,2,2); g.fillRect(18,13,2,2);
      g.fillStyle(0x7d4a2a); g.fillRect(12,22,4,7); g.fillRect(18,22,4,7);
    });
    make('boss', g => {
      g.fillStyle(0x5a261c); g.fillRect(5,7,22,20); g.fillStyle(0xbf6c2f); g.fillRect(8,4,16,9);
      g.fillStyle(0xffc18a); g.fillRect(9,11,14,8); g.fillStyle(0x111111); g.fillRect(12,13,3,3); g.fillRect(18,13,3,3);
      g.fillStyle(0xff4f4f); g.fillRect(10,20,12,3); g.fillStyle(0xcaa15a); g.fillRect(2,15,6,3); g.fillRect(24,15,6,3);
    });
    make('genie', g => {
      g.fillStyle(0x2f8f49); g.fillRect(0,0,32,32);
      g.fillStyle(0x3aa6ff); g.fillRect(10,7,12,12); g.fillRect(12,19,8,5); g.fillRect(14,23,12,4);
      g.fillStyle(0x7bd5ff); g.fillRect(12,9,8,4);
      g.fillStyle(0xffd36b); g.fillRect(9,5,14,3);
    });
    make('crystal', g => {
      g.fillStyle(0x173850); g.fillRect(0,0,32,32);
      g.fillStyle(0x57c7ff); g.fillRect(12,4,8,4); g.fillRect(8,8,16,8); g.fillStyle(0x2c84ff); g.fillRect(10,16,12,6); g.fillRect(13,22,6,6);
      g.fillStyle(0xbdf2ff); g.fillRect(13,8,5,8);
    });

    g.destroy();
  }
}

class TitleScene extends Phaser.Scene {
  constructor() { super('Title'); }
  create() {
    this.cameras.main.setBackgroundColor('#10331f');
    this.add.rectangle(GAME_W/2, WORLD_H/2, GAME_W, WORLD_H, 0x10331f);
    this.add.text(GAME_W/2, 80, 'DINO HANGRY ROCKS', { fontFamily: 'monospace', fontSize: '38px', color: COLORS.gold, stroke: '#000', strokeThickness: 6 }).setOrigin(0.5);
    this.add.text(GAME_W/2, 135, '8-bit forest adventure', { fontFamily: 'monospace', fontSize: '18px', color: COLORS.text }).setOrigin(0.5);
    this.add.image(GAME_W/2 - 42, 210, 'dino').setScale(3);
    this.add.image(GAME_W/2 + 45, 210, 'rock').setScale(3);
    const instructions = [
      'Walk through the forest as a hungry T-Rex.',
      'Smash rocks to find food before energy runs out.',
      'Cavemen and the genie try to stop you.',
      'At Level 6, the ninja joins your team.',
      'Every 10 levels has a boss battle.',
      'Between levels, solve the crystal puzzle.'
    ];
    this.add.text(GAME_W/2, 310, instructions.join('\n'), { fontFamily: 'monospace', fontSize: '16px', color: COLORS.text, align: 'center', lineSpacing: 8 }).setOrigin(0.5);
    this.add.text(GAME_W/2, 430, 'Press SPACE or click to start', { fontFamily: 'monospace', fontSize: '20px', color: COLORS.green, stroke: '#000', strokeThickness: 4 }).setOrigin(0.5);
    this.input.keyboard.once('keydown-SPACE', () => this.scene.start('Game', { level: 1, wins: 0, losses: 0, xp: 0 }));
    this.input.once('pointerdown', () => this.scene.start('Game', { level: 1, wins: 0, losses: 0, xp: 0 }));
  }
}

class GameScene extends Phaser.Scene {
  constructor() { super('Game'); }
  init(data) {
    this.level = data.level || 1;
    this.wins = data.wins || 0;
    this.losses = data.losses || 0;
    this.xp = data.xp || 0;
    this.isBossLevel = this.level % 10 === 0;
  }
  create() {
    this.cameras.main.setBackgroundColor('#0e2d1d');
    this.cursors = this.input.keyboard.createCursorKeys();
    this.keys = this.input.keyboard.addKeys('W,A,S,D,SPACE,ENTER');
    this.busy = false;
    this.log = [];

    this.buildLevel();
    this.drawWorld();
    this.drawUI();
    this.addLog('🧞 The genie scattered rocks through the forest!');

    this.input.keyboard.on('keydown', (event) => {
      if (this.busy) return;
      const k = event.key.toLowerCase();
      if (k === 'arrowup' || k === 'w') this.tryMove(0, -1);
      else if (k === 'arrowdown' || k === 's') this.tryMove(0, 1);
      else if (k === 'arrowleft' || k === 'a') this.tryMove(-1, 0);
      else if (k === 'arrowright' || k === 'd') this.tryMove(1, 0);
      else if (k === ' ' || k === 'enter') this.stompNearby();
    });

    this.createTouchControls();
  }

  buildLevel() {
    const lvl = this.level;
    this.player = { x: 1, y: MAP_ROWS - 2, hp: 36 + Math.floor(lvl * 1.8), maxHp: 36 + Math.floor(lvl * 1.8), food: 0 };
    this.moves = Math.max(24, 42 - Math.floor(lvl * 0.25));
    this.foodNeeded = Math.min(8, 2 + Math.floor(lvl / 8));
    this.ninjaUnlocked = lvl >= 6;
    this.ninjaHp = this.ninjaUnlocked ? 16 + Math.floor(lvl * 0.8) : 0;
    this.ninjaPos = this.ninjaUnlocked ? { x: 2, y: MAP_ROWS - 2 } : null;
    this.map = [];
    this.rocks = new Map();
    this.enemies = [];
    this.foodSpots = new Set();
    this.decor = new Map();

    for (let y = 0; y < MAP_ROWS; y++) {
      const row = [];
      for (let x = 0; x < MAP_COLS; x++) {
        const edge = x === 0 || y === 0 || x === MAP_COLS - 1 || y === MAP_ROWS - 1;
        const tree = edge || Math.random() < 0.09;
        row.push(tree ? 'tree' : 'grass');
        this.decor.set(key(x, y), Math.random() < 0.5 ? 'tile_grass1' : 'tile_grass2');
      }
      this.map.push(row);
    }

    this.map[this.player.y][this.player.x] = 'grass';
    this.map[MAP_ROWS-2][2] = 'grass';
    this.genie = { x: MAP_COLS - 3, y: 2 };
    this.map[this.genie.y][this.genie.x] = 'grass';

    const rockCount = clamp(5 + Math.floor(lvl * 0.45), 5, 25);
    const enemyCount = this.isBossLevel ? 2 + Math.floor(lvl / 20) : clamp(1 + Math.floor(lvl / 7), 1, 8);
    const rockHp = 3 + Math.floor(lvl * 0.8);

    for (let i = 0; i < rockCount; i++) {
      const p = this.emptySpotFarFromPlayer();
      const hp = rockHp + randInt(0, Math.floor(lvl / 8));
      this.rocks.set(key(p.x, p.y), { x: p.x, y: p.y, hp, maxHp: hp, hard: lvl >= 12 && Math.random() < 0.45 });
    }

    const rockKeys = Array.from(this.rocks.keys());
    Phaser.Utils.Array.Shuffle(rockKeys);
    for (let i = 0; i < Math.min(this.foodNeeded + 1, rockKeys.length); i++) this.foodSpots.add(rockKeys[i]);

    for (let i = 0; i < enemyCount; i++) {
      const p = this.emptySpotFarFromPlayer();
      this.enemies.push({ x: p.x, y: p.y, hp: 8 + Math.floor(lvl * 1.1), maxHp: 8 + Math.floor(lvl * 1.1), kind: 'caveman' });
    }
    if (this.isBossLevel) {
      const p = { x: MAP_COLS - 4, y: 3 };
      this.enemies.push({ x: p.x, y: p.y, hp: 45 + lvl * 4, maxHp: 45 + lvl * 4, kind: 'boss' });
      this.addLog('👑 Boss level! Defeat the mighty hunter.');
    }
  }

  emptySpotFarFromPlayer() {
    for (let tries = 0; tries < 500; tries++) {
      const x = randInt(2, MAP_COLS - 3);
      const y = randInt(2, MAP_ROWS - 3);
      const p = { x, y };
      if (this.map[y][x] !== 'grass') continue;
      if (manhattan(p, this.player) < 5) continue;
      if (samePos(p, this.genie)) continue;
      if (this.rocks.has(key(x, y))) continue;
      if (this.enemies.some(e => e.x === x && e.y === y)) continue;
      return p;
    }
    return { x: randInt(2, MAP_COLS - 3), y: randInt(2, MAP_ROWS - 3) };
  }

  drawWorld() {
    this.worldLayer?.destroy();
    this.worldLayer = this.add.container(0, 0);
    for (let y = 0; y < MAP_ROWS; y++) {
      for (let x = 0; x < MAP_COLS; x++) {
        const tx = x * TILE + TILE / 2;
        const ty = y * TILE + TILE / 2;
        const base = this.map[y][x] === 'tree' ? 'tree' : this.decor.get(key(x,y));
        this.worldLayer.add(this.add.image(tx, ty, base));
      }
    }
    this.worldLayer.add(this.add.image(this.genie.x*TILE + TILE/2, this.genie.y*TILE + TILE/2, 'genie'));

    for (const r of this.rocks.values()) {
      this.worldLayer.add(this.add.image(r.x*TILE + TILE/2, r.y*TILE + TILE/2, r.hard ? 'hardrock' : 'rock'));
      this.worldLayer.add(this.add.text(r.x*TILE + 18, r.y*TILE + 20, String(r.hp), { fontFamily: 'monospace', fontSize: '10px', color: '#ffffff', stroke: '#000', strokeThickness: 2 }));
    }

    for (const e of this.enemies) {
      this.worldLayer.add(this.add.image(e.x*TILE + TILE/2, e.y*TILE + TILE/2, e.kind === 'boss' ? 'boss' : 'caveman'));
      this.worldLayer.add(this.add.text(e.x*TILE + 2, e.y*TILE + 1, String(e.hp), { fontFamily: 'monospace', fontSize: '10px', color: '#ffef9c', stroke: '#000', strokeThickness: 2 }));
    }

    if (this.ninjaUnlocked && this.ninjaHp > 0 && this.ninjaPos) {
      this.worldLayer.add(this.add.image(this.ninjaPos.x*TILE + TILE/2, this.ninjaPos.y*TILE + TILE/2, 'ninja'));
    }

    this.playerSprite = this.add.image(this.player.x*TILE + TILE/2, this.player.y*TILE + TILE/2, 'dino').setDepth(10);
    this.worldLayer.add(this.playerSprite);
  }

  drawUI() {
    this.uiLayer?.destroy();
    this.uiLayer = this.add.container(0, GAME_H);
    this.uiLayer.add(this.add.rectangle(GAME_W/2, UI_H/2, GAME_W, UI_H, COLORS.panel));
    this.uiLayer.add(this.add.rectangle(GAME_W/2, 4, GAME_W, 8, 0x215b3c));

    const title = this.isBossLevel ? `LEVEL ${this.level}: BOSS HUNTER BATTLE` : `LEVEL ${this.level}: FOREST ROCK SMASH`;
    this.uiLayer.add(this.add.text(14, 18, title, { fontFamily: 'monospace', fontSize: '18px', color: COLORS.gold, stroke: '#000', strokeThickness: 3 }));
    const ninja = this.ninjaUnlocked ? `🥷 ${this.ninjaHp} HP` : '🥷 locked until L6';
    const hud = `🦖 HP ${this.player.hp}/${this.player.maxHp}   🍖 Food ${this.player.food}/${this.foodNeeded}   👣 Moves ${this.moves}   ⭐ XP ${this.xp}   ${ninja}`;
    this.uiLayer.add(this.add.text(14, 46, hud, { fontFamily: 'monospace', fontSize: '14px', color: COLORS.text }));
    this.uiLayer.add(this.add.text(14, 76, 'Move: Arrow Keys/WASD  •  Stomp/Attack: Space or Enter  •  Touch buttons also work', { fontFamily: 'monospace', fontSize: '13px', color: '#c8ffd0' }));

    const logText = this.log.slice(-3).join('\n');
    this.uiLayer.add(this.add.text(14, 103, logText, { fontFamily: 'monospace', fontSize: '13px', color: '#ffffff', wordWrap: { width: GAME_W - 28 } }));
  }

  createTouchControls() {
    const makeBtn = (x, y, label, cb) => {
      const rect = this.add.rectangle(x, y, 46, 34, 0xfff2ca).setInteractive({ useHandCursor: true }).setScrollFactor(0).setDepth(50);
      rect.setStrokeStyle(3, 0x7f5b20);
      const text = this.add.text(x, y, label, { fontFamily: 'monospace', fontSize: '18px', color: '#1f2b1f' }).setOrigin(0.5).setDepth(51);
      rect.on('pointerdown', cb);
      return [rect, text];
    };
    makeBtn(GAME_W - 78, GAME_H + 32, '↑', () => this.tryMove(0,-1));
    makeBtn(GAME_W - 124, GAME_H + 70, '←', () => this.tryMove(-1,0));
    makeBtn(GAME_W - 78, GAME_H + 70, '⚡', () => this.stompNearby());
    makeBtn(GAME_W - 32, GAME_H + 70, '→', () => this.tryMove(1,0));
    makeBtn(GAME_W - 78, GAME_H + 108, '↓', () => this.tryMove(0,1));
  }

  isBlocked(x, y) {
    if (x < 0 || y < 0 || x >= MAP_COLS || y >= MAP_ROWS) return true;
    if (this.map[y][x] === 'tree') return true;
    return false;
  }

  tryMove(dx, dy) {
    if (this.busy || this.moves <= 0) return;
    const nx = this.player.x + dx;
    const ny = this.player.y + dy;
    if (this.isBlocked(nx, ny)) { this.addLog('🌳 Trees block the path.'); return; }

    const rock = this.rocks.get(key(nx, ny));
    const enemy = this.enemies.find(e => e.x === nx && e.y === ny);
    if (rock) this.damageRock(rock);
    else if (enemy) this.damageEnemy(enemy);
    else {
      this.player.x = nx; this.player.y = ny;
      this.moves--;
      this.addLog('🦖 T-Rex stomp-stomps through the forest.');
    }
    this.afterPlayerAction();
  }

  stompNearby() {
    if (this.busy || this.moves <= 0) return;
    const dirs = [{x:0,y:-1},{x:0,y:1},{x:-1,y:0},{x:1,y:0}];
    let bestEnemy = null;
    for (const d of dirs) {
      const e = this.enemies.find(e => e.x === this.player.x + d.x && e.y === this.player.y + d.y);
      if (e) { bestEnemy = e; break; }
    }
    if (bestEnemy) this.damageEnemy(bestEnemy);
    else {
      let bestRock = null;
      for (const d of dirs) {
        const r = this.rocks.get(key(this.player.x + d.x, this.player.y + d.y));
        if (r) { bestRock = r; break; }
      }
      if (bestRock) this.damageRock(bestRock);
      else { this.addLog('⚡ Nothing nearby to stomp.'); return; }
    }
    this.afterPlayerAction();
  }

  damageRock(rock) {
    const dmg = 2 + Math.floor(this.level / 9) + (this.ninjaUnlocked && this.ninjaHp > 0 ? 1 : 0);
    rock.hp -= dmg;
    this.moves--;
    this.addLog(`🪨 T-Rex smashes rock for ${dmg}!`);
    if (rock.hp <= 0) {
      const k = key(rock.x, rock.y);
      this.rocks.delete(k);
      if (this.foodSpots.has(k)) {
        this.player.food++;
        this.foodSpots.delete(k);
        this.addLog('🍖 Food found! Hangry level goes down.');
      } else {
        this.addLog('💨 Just dusty pebbles here.');
      }
    }
  }

  damageEnemy(enemy) {
    const dinoDmg = 4 + Math.floor(this.level / 7);
    const ninjaDmg = this.ninjaUnlocked && this.ninjaHp > 0 ? 3 + Math.floor(this.level / 12) : 0;
    enemy.hp -= dinoDmg + ninjaDmg;
    this.moves--;
    this.addLog(`⚔️ Team attacks for ${dinoDmg + ninjaDmg}!`);
    if (enemy.hp <= 0) {
      this.enemies = this.enemies.filter(e => e !== enemy);
      this.xp += enemy.kind === 'boss' ? 25 : 5;
      this.addLog(enemy.kind === 'boss' ? '👑 Boss defeated!' : '🧔 Caveman runs away!');
    }
  }

  afterPlayerAction() {
    this.enemyTurn();
    this.genieTurn();
    this.drawWorld();
    this.drawUI();
    this.checkEnd();
  }

  enemyTurn() {
    for (const e of this.enemies) {
      if (manhattan(e, this.player) === 1) {
        const dmg = e.kind === 'boss' ? 5 : 2;
        this.player.hp -= dmg;
        this.addLog(e.kind === 'boss' ? `🏹 Boss hunter hits Dino for ${dmg}.` : `🏹 Caveman pokes Dino for ${dmg}.`);
        continue;
      }
      const dx = Math.sign(this.player.x - e.x);
      const dy = Math.sign(this.player.y - e.y);
      const options = Math.abs(this.player.x - e.x) > Math.abs(this.player.y - e.y) ? [{x:dx,y:0},{x:0,y:dy}] : [{x:0,y:dy},{x:dx,y:0}];
      for (const o of options) {
        const nx = e.x + o.x, ny = e.y + o.y;
        if (o.x === 0 && o.y === 0) continue;
        if (this.isBlocked(nx, ny)) continue;
        if (this.rocks.has(key(nx, ny))) continue;
        if (this.enemies.some(other => other !== e && other.x === nx && other.y === ny)) continue;
        if (nx === this.player.x && ny === this.player.y) continue;
        e.x = nx; e.y = ny; break;
      }
    }
  }

  genieTurn() {
    if (Math.random() > 0.18 + this.level * 0.003) return;
    const p = this.emptySpotFarFromPlayer();
    const hp = 3 + Math.floor(this.level * 0.65);
    this.rocks.set(key(p.x, p.y), { x:p.x, y:p.y, hp, maxHp:hp, hard: true });
    this.addLog('🧞 Genie poofs in another rock!');
  }

  addLog(msg) {
    this.log.push(msg);
    if (this.log.length > 8) this.log.shift();
  }

  checkEnd() {
    if (this.player.hp <= 0 || this.moves <= 0) {
      this.busy = true;
      this.time.delayedCall(500, () => this.scene.start('GameOver', { won:false, level:this.level, wins:this.wins, losses:this.losses+1, xp:this.xp }));
      return;
    }
    const bossAlive = this.isBossLevel && this.enemies.some(e => e.kind === 'boss');
    if (this.player.food >= this.foodNeeded && !bossAlive) {
      this.busy = true;
      this.wins++;
      this.time.delayedCall(500, () => this.scene.start('Puzzle', { level:this.level, wins:this.wins, losses:this.losses, xp:this.xp + 3 }));
    }
  }
}

class PuzzleScene extends Phaser.Scene {
  constructor() { super('Puzzle'); }
  init(data) { this.level = data.level; this.wins = data.wins; this.losses = data.losses; this.xp = data.xp; }
  create() {
    this.cameras.main.setBackgroundColor('#132a44');
    this.remaining = Math.max(7, 16 - Math.floor(this.level / 5));
    this.pieces = [];
    this.add.text(GAME_W/2, 55, 'CRYSTAL PUZZLE', { fontFamily:'monospace', fontSize:'34px', color:'#bdf2ff', stroke:'#000', strokeThickness:6 }).setOrigin(0.5);
    this.add.text(GAME_W/2, 96, 'Click all broken crystal pieces before time runs out!', { fontFamily:'monospace', fontSize:'15px', color:COLORS.text }).setOrigin(0.5);
    this.timerText = this.add.text(GAME_W/2, 130, '', { fontFamily:'monospace', fontSize:'20px', color:COLORS.gold }).setOrigin(0.5);
    const count = clamp(4 + Math.floor(this.level / 4), 4, 14);
    for (let i=0; i<count; i++) {
      const x = randInt(80, GAME_W - 80), y = randInt(175, GAME_H - 50);
      const s = this.add.image(x, y, 'crystal').setScale(1.25).setInteractive({ useHandCursor:true });
      s.angle = randInt(-20,20);
      s.on('pointerdown', () => { s.destroy(); this.pieces = this.pieces.filter(p => p !== s); this.checkPuzzleWin(); });
      this.pieces.push(s);
    }
    this.time.addEvent({ delay:1000, loop:true, callback:() => { this.remaining--; this.updateTimer(); if (this.remaining <= 0) this.puzzleDone(false); } });
    this.updateTimer();
  }
  updateTimer() { this.timerText.setText(`Time: ${this.remaining}`); }
  checkPuzzleWin() { if (this.pieces.length === 0) this.puzzleDone(true); }
  puzzleDone(success) {
    if (this.done) return;
    this.done = true;
    const next = Math.min(50, this.level + 1);
    this.xp += success ? 5 : 1;
    const msg = success ? '💎 Crystal fixed! Bonus XP!' : '⏰ Crystal still sparkles, but time ran out.';
    this.add.text(GAME_W/2, WORLD_H - 95, msg, { fontFamily:'monospace', fontSize:'18px', color:success ? COLORS.green : COLORS.red, stroke:'#000', strokeThickness:4 }).setOrigin(0.5);
    this.time.delayedCall(1200, () => {
      if (this.level >= 50) this.scene.start('Victory', { wins:this.wins, losses:this.losses, xp:this.xp });
      else this.scene.start('Game', { level:next, wins:this.wins, losses:this.losses, xp:this.xp });
    });
  }
}

class GameOverScene extends Phaser.Scene {
  constructor() { super('GameOver'); }
  init(data) { Object.assign(this, data); }
  create() {
    this.cameras.main.setBackgroundColor('#2b1818');
    this.add.text(GAME_W/2, 120, 'TRY AGAIN!', { fontFamily:'monospace', fontSize:'42px', color:'#ff9a8a', stroke:'#000', strokeThickness:7 }).setOrigin(0.5);
    this.add.text(GAME_W/2, 210, `Level ${this.level} was too spicy for Dino.`, { fontFamily:'monospace', fontSize:'18px', color:COLORS.text }).setOrigin(0.5);
    this.add.text(GAME_W/2, 275, 'Press SPACE to restart this level\nClick to return to title', { fontFamily:'monospace', fontSize:'18px', color:COLORS.gold, align:'center', lineSpacing:10 }).setOrigin(0.5);
    this.input.keyboard.once('keydown-SPACE', () => this.scene.start('Game', { level:this.level, wins:this.wins, losses:this.losses, xp:this.xp }));
    this.input.once('pointerdown', () => this.scene.start('Title'));
  }
}

class VictoryScene extends Phaser.Scene {
  constructor() { super('Victory'); }
  init(data) { Object.assign(this, data); }
  create() {
    this.cameras.main.setBackgroundColor('#102f45');
    this.add.text(GAME_W/2, 120, 'DINO LEGEND!', { fontFamily:'monospace', fontSize:'44px', color:COLORS.gold, stroke:'#000', strokeThickness:7 }).setOrigin(0.5);
    this.add.image(GAME_W/2, 210, 'dino').setScale(4);
    this.add.text(GAME_W/2, 320, `You cleared the first 50 levels!\nWins: ${this.wins}   Losses: ${this.losses}   XP: ${this.xp}`, { fontFamily:'monospace', fontSize:'18px', color:COLORS.text, align:'center', lineSpacing:10 }).setOrigin(0.5);
    this.add.text(GAME_W/2, 420, 'Click to play again', { fontFamily:'monospace', fontSize:'20px', color:COLORS.green, stroke:'#000', strokeThickness:4 }).setOrigin(0.5);
    this.input.once('pointerdown', () => this.scene.start('Title'));
  }
}

const config = {
  type: Phaser.AUTO,
  parent: 'game-wrap',
  width: GAME_W,
  height: WORLD_H,
  backgroundColor: '#0f2f1f',
  pixelArt: true,
  roundPixels: true,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  scene: [BootScene, TitleScene, GameScene, PuzzleScene, GameOverScene, VictoryScene]
};

window.addEventListener('load', () => {
  if (!window.Phaser) {
    document.getElementById('game-wrap').innerHTML = '<div class="fallback"><h1>Phaser did not load.</h1><p>Check your internet connection or download Phaser locally. The game uses a CDN link in index.html.</p></div>';
    return;
  }
  new Phaser.Game(config);
});
