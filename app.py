<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Dino Hangry Rocks — Forest Run</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/phaser/3.70.0/phaser.min.js"></script>
<style>
  :root{
    --ink:#132015; --cream:#fef6e4; --leaf:#3ea65c; --deep:#0b3b24;
    --amber:#ffb84d; --ember:#ff6b4a; --panel:rgba(11,42,26,0.82);
  }
  *{box-sizing:border-box;}
  html,body{margin:0;padding:0;height:100%;background:#07160d;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;overflow:hidden;}
  #root{position:relative;width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;background:#07160d;}
  #game-container{width:100%;height:100%;max-width:1280px;max-height:720px;position:relative;box-shadow:0 0 60px rgba(0,0,0,0.6);}
  #game-container canvas{width:100% !important;height:100% !important;}

  /* ---------- HUD ---------- */
  #hud{position:absolute;top:0;left:0;right:0;padding:10px 14px;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;z-index:5;font-weight:700;}
  .hud-group{display:flex;flex-direction:column;gap:6px;pointer-events:none;}
  .bar-row{display:flex;align-items:center;gap:6px;background:var(--panel);padding:5px 10px;border-radius:999px;border:2px solid rgba(255,255,255,0.15);color:var(--cream);font-size:13px;backdrop-filter:blur(2px);}
  .bar-track{width:110px;height:9px;border-radius:6px;background:rgba(0,0,0,0.4);overflow:hidden;border:1px solid rgba(255,255,255,0.2);}
  .bar-fill{height:100%;border-radius:6px;transition:width .25s ease;}
  .fill-dino{background:linear-gradient(90deg,#7ee08a,#2fae52);}
  .fill-ninja{background:linear-gradient(90deg,#cfd8ff,#7d8dff);}
  .fill-boss{background:linear-gradient(90deg,#ffb84d,#ff5a3d);}
  #food-count, #time-count, #level-count{background:var(--panel);color:var(--cream);padding:6px 12px;border-radius:999px;border:2px solid rgba(255,255,255,0.15);font-size:13px;}
  #time-count.low{color:#ffb0a0;animation:pulse 0.6s infinite;}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
  #toast{position:absolute;top:66px;left:50%;transform:translateX(-50%);background:rgba(10,20,12,0.88);color:#fef6e4;padding:8px 18px;border-radius:12px;font-size:14px;font-weight:600;border:1px solid rgba(255,255,255,0.15);z-index:5;pointer-events:none;opacity:0;transition:opacity .3s;max-width:80%;text-align:center;}

  /* ---------- Touch controls ---------- */
  #touch-controls{position:absolute;bottom:0;left:0;right:0;display:flex;justify-content:space-between;align-items:flex-end;padding:14px;pointer-events:none;z-index:6;}
  .pad{display:flex;gap:10px;pointer-events:auto;}
  .btn{width:58px;height:58px;border-radius:16px;background:rgba(255,255,255,0.85);border:2px solid rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;color:#132015;user-select:none;touch-action:none;box-shadow:0 4px 10px rgba(0,0,0,0.3);}
  .btn:active{background:#ffe08a;transform:translateY(2px);}
  .btn.wide{width:74px;}
  .btn.action{background:#ff8a5b;color:#2a1206;}
  .btn.roar{background:#8fd0ff;}

  /* ---------- Overlays ---------- */
  .overlay{position:absolute;inset:0;background:radial-gradient(ellipse at center, rgba(10,30,16,0.92) 0%, rgba(4,14,7,0.97) 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:var(--cream);z-index:10;padding:24px;}
  .hidden{display:none !important;}
  .panel{background:rgba(255,255,255,0.05);border:2px solid rgba(255,255,255,0.15);border-radius:20px;padding:28px 30px;max-width:520px;backdrop-filter:blur(3px);}
  .panel h1{margin:0 0 6px;font-size:clamp(26px,5vw,38px);letter-spacing:0.5px;}
  .panel h2{margin:0 0 14px;font-size:clamp(18px,3.4vw,24px);color:var(--amber);}
  .panel p{line-height:1.5;font-size:15px;color:#e8f5e6;}
  .panel ul{text-align:left;font-size:14px;line-height:1.6;color:#d9ecd6;}
  .cta{margin-top:16px;background:linear-gradient(180deg,#ffe08a,#ffb84d);color:#2a1206;border:none;border-radius:14px;padding:14px 26px;font-size:17px;font-weight:800;cursor:pointer;box-shadow:0 6px 16px rgba(0,0,0,0.35);}
  .cta:hover{filter:brightness(1.06);}
  .cta.secondary{background:linear-gradient(180deg,#d9e6ff,#a9c2ff);margin-left:10px;}
  .stat-row{display:flex;gap:18px;justify-content:center;margin-top:10px;font-size:14px;color:#cfe8cf;}
  #hint{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,0.55);font-size:11px;z-index:6;}
</style>
</head>
<body>
<div id="root">
  <div id="game-container"></div>

  <div id="hud">
    <div class="hud-group">
      <div class="bar-row">🦖 <div class="bar-track"><div id="dino-fill" class="bar-fill fill-dino" style="width:100%"></div></div></div>
      <div class="bar-row" id="ninja-row">🥷 <div class="bar-track"><div id="ninja-fill" class="bar-fill fill-ninja" style="width:100%"></div></div></div>
      <div class="bar-row hidden" id="boss-row">👑 <div class="bar-track"><div id="boss-fill" class="bar-fill fill-boss" style="width:100%"></div></div></div>
    </div>
    <div class="hud-group" style="align-items:flex-end;">
      <div id="level-count">Level 1</div>
      <div id="food-count">🍖 0 / 3</div>
      <div id="time-count">⏱ 60s</div>
    </div>
  </div>
  <div id="toast"></div>

  <div id="touch-controls">
    <div class="pad">
      <div class="btn wide" id="btn-left">◀</div>
      <div class="btn wide" id="btn-right">▶</div>
      <div class="btn" id="btn-jump">⤒</div>
    </div>
    <div class="pad">
      <div class="btn roar" id="btn-roar">📣</div>
      <div class="btn action" id="btn-attack">👊</div>
    </div>
  </div>
  <div id="hint">Arrow keys / A-D to move · Up or Space to jump · Z or 👊 to smash/attack · X or 📣 to roar</div>

  <div class="overlay" id="overlay-start">
    <div class="panel">
      <h1>🦖 Dino Hangry Rocks</h1>
      <h2>Forest Run</h2>
      <p>A hungry T-Rex is running through the forest looking for food. A mischievous genie hides snacks under rocks and keeps summoning more rocks to block the trail. A caveman tribe wants the food too — and won't hesitate to attack. Luckily, a ninja friend joins the run once you get going.</p>
      <ul>
        <li>Run right, smash rocks blocking your path for a chance at hidden food</li>
        <li>Bump into cavemen to fight — or use Dino Roar to scare off a crowd</li>
        <li>Reach the glowing portal once you've found enough food</li>
        <li>Watch out for boss hunters every 10th level!</li>
      </ul>
      <button class="cta" id="btn-start">▶ Start Adventure</button>
    </div>
  </div>

  <div class="overlay hidden" id="overlay-win">
    <div class="panel">
      <h1>🎉 Level Cleared!</h1>
      <p id="win-text">The T-Rex found enough food and calmed down.</p>
      <div class="stat-row" id="win-stats"></div>
      <button class="cta" id="btn-next">Next Level ▶</button>
    </div>
  </div>

  <div class="overlay hidden" id="overlay-lose">
    <div class="panel">
      <h1 id="lose-title">😵 Oh No!</h1>
      <p id="lose-text">The T-Rex got too tired.</p>
      <button class="cta" id="btn-retry">Retry Level</button>
      <button class="cta secondary" id="btn-restart">New Game</button>
    </div>
  </div>

  <div class="overlay hidden" id="overlay-finish">
    <div class="panel">
      <h1>🏆 Forest Champion!</h1>
      <p>You made it through all 50 levels of the forest run!</p>
      <button class="cta" id="btn-restart2">Play Again</button>
    </div>
  </div>
</div>

<script>
/* ============================= CONFIG / BALANCE ============================= */
const MAX_LEVEL = 50;
const NINJA_UNLOCK_LEVEL = 6;
const BOSS_INTERVAL = 10;
const FOODS = ['🍖','🥩','🍗','🍉','🍌','🥥'];
const ROCK_KINDS = ['🪨','⛰️','🧱'];
const GROUND_Y = 470;
const WORLD_H = 540;

function cfgFor(level){
  const tier = Math.floor((level - 1) / 10);
  const isBoss = level % BOSS_INTERVAL === 0;
  return {
    level,
    levelWidth: Math.min(5400, 2100 + level * 60),
    rockCount: 6 + Math.min(14, Math.floor(level / 2)),
    rockHp: 5 + tier * 2 + Math.min(10, Math.floor(level / 5)),
    foodGoal: 3 + Math.min(7, Math.floor(level / 7)),
    cavemenCount: 2 + Math.min(9, Math.floor(level / 5)) + (isBoss ? 2 : 0),
    dinoMaxHp: 70 + Math.min(60, level * 1.4),
    ninjaMaxHp: level < NINJA_UNLOCK_LEVEL ? 0 : 34 + Math.min(46, level),
    timeLimit: 65 + Math.max(0, 22 - tier * 5) + (isBoss ? 25 : 0),
    genieChancePerSec: Math.min(0.05, 0.010 + level * 0.0006),
    bossHp: isBoss ? 70 + level * 6 : 0,
    isBoss,
  };
}

/* ============================= GLOBAL STATE ============================= */
const STATE = { level: 1, wins: 0, losses: 0, xp: 0 };

function toast(msg, ms=1800){
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.style.opacity = 1;
  clearTimeout(el._t);
  el._t = setTimeout(()=>{ el.style.opacity = 0; }, ms);
}

/* ============================= PHASER SCENE ============================= */
class PlayScene extends Phaser.Scene{
  constructor(){ super('Play'); }

  init(data){
    this.level = data.level || STATE.level;
    this.cfg = cfgFor(this.level);
  }

  preload(){}

  create(){
    const cfg = this.cfg;
    this.worldW = cfg.levelWidth;
    this.physics.world.setBounds(0,0,this.worldW, WORLD_H);
    this.cameras.main.setBounds(0,0,this.worldW, WORLD_H);
    this.cameras.main.setBackgroundColor('#bdeeb0');

    this.buildTextures();
    this.buildParallax();
    this.buildGround();

    this.rocks = [];
    this.enemies = [];
    this.foodFound = 0;
    this.gameOver = false;
    this.timeLeft = cfg.timeLimit;
    this.attackCooldown = 0;
    this.roarCooldown = 0;
    this.facing = 1;

    // ---- Player (T-Rex) ----
    this.player = this.add.text(120, GROUND_Y - 10, '🦖', {fontSize:'52px'}).setOrigin(0.5,1);
    this.physics.add.existing(this.player);
    this.player.body.setSize(34,44).setOffset(-17,-40);
    this.player.body.setCollideWorldBounds(true);
    this.player.body.setDragX(1400);
    this.player.body.setMaxVelocity(230, 900);
    this.player.dinoHp = cfg.dinoMaxHp;
    this.player.dinoMaxHp = cfg.dinoMaxHp;

    this.physics.add.collider(this.player, this.groundBody);

    // ---- Ninja companion ----
    this.ninja = null;
    if (this.level >= NINJA_UNLOCK_LEVEL){
      this.ninja = this.add.text(60, GROUND_Y - 10, '🥷', {fontSize:'40px'}).setOrigin(0.5,1);
      this.physics.add.existing(this.ninja);
      this.ninja.body.setAllowGravity(false);
      this.ninja.hp = cfg.ninjaMaxHp;
      this.ninja.maxHp = cfg.ninjaMaxHp;
      this.ninja.atkCd = 0;
    }

    // ---- Genie ----
    this.genie = this.add.text(400, 140, '🧞', {fontSize:'46px'}).setOrigin(0.5,1);
    this.genieBaseY = 140;

    // ---- Rocks & enemies spawn ----
    this.spawnRocks(cfg);
    this.spawnEnemies(cfg);

    // ---- Boss ----
    this.boss = null;
    if (cfg.isBoss){
      const bx = this.worldW - 420;
      this.boss = this.add.text(bx, GROUND_Y - 10, '👑🧔', {fontSize:'54px'}).setOrigin(0.5,1);
      this.physics.add.existing(this.boss);
      this.boss.body.setSize(46,50).setOffset(-23,-46);
      this.boss.body.setCollideWorldBounds(true);
      this.boss.hp = cfg.bossHp; this.boss.maxHp = cfg.bossHp;
      this.boss.isEnemy = true; this.boss.enemyType = 'boss'; this.boss.atkCd = 0;
      this.physics.add.collider(this.boss, this.groundBody);
      this.enemies.push(this.boss);
    }

    // ---- Portal ----
    this.portal = this.add.text(this.worldW - 110, GROUND_Y - 6, '🌀', {fontSize:'56px'}).setOrigin(0.5,1);
    this.physics.add.existing(this.portal, true);

    // ---- Camera ----
    this.cameras.main.startFollow(this.player, true, 0.09, 0.09, -170, 0);

    // ---- Input ----
    this.cursors = this.input.keyboard.createCursorKeys();
    this.keys = this.input.keyboard.addKeys({W:'W',A:'A',S:'S',D:'D',Z:'Z',X:'X',SPACE:'SPACE'});
    this.bindTouchControls();

    // ---- HUD init ----
    this.refreshHud();
    document.getElementById('food-count').textContent = `🍖 ${this.foodFound} / ${cfg.foodGoal}`;
    document.getElementById('level-count').textContent = `Level ${this.level}${cfg.isBoss ? ' 👑' : ''}`;
    document.getElementById('boss-row').classList.toggle('hidden', !cfg.isBoss);
    document.getElementById('ninja-row').style.opacity = this.level >= NINJA_UNLOCK_LEVEL ? 1 : 0.35;

    toast(cfg.isBoss ? '👑 Boss level! A tough hunter blocks the trail ahead.' : `Level ${this.level}: run, smash rocks, and find ${cfg.foodGoal} food!`, 2600);

    // ---- Timer ----
    this.time.addEvent({ delay: 1000, loop: true, callback: () => this.tickTime() });
  }

  buildTextures(){
    if (this.textures.exists('sky')) return;
    const g = this.add.graphics();

    // sky gradient
    g.clear();
    for(let i=0;i<WORLD_H;i++){
      const t = i/WORLD_H;
      const c = Phaser.Display.Color.Interpolate.ColorWithColor(
        Phaser.Display.Color.ValueToColor('#bdeeb0'),
        Phaser.Display.Color.ValueToColor('#eafff0'), 100, t*100);
      g.fillStyle(Phaser.Display.Color.GetColor(c.r,c.g,c.b),1);
      g.fillRect(0,i,64,1);
    }
    g.generateTexture('sky',64,WORLD_H);
    g.clear();

    // distant hills
    g.fillStyle(0x2c8a53,1);
    g.fillEllipse(200,470,420,220);
    g.fillEllipse(560,470,420,220);
    g.generateTexture('hills',760,260);
    g.clear();

    // mid trees
    g.fillStyle(0x1f7a45,1);
    for(let x=0; x<420; x+=70){
      g.fillTriangle(x,220, x+40,60, x+80,220);
    }
    g.generateTexture('midtrees',460,220);
    g.clear();

    // foreground foliage
    g.fillStyle(0x0e5a30,1);
    for(let x=0; x<420; x+=60){
      g.fillCircle(x+20, 150, 46);
      g.fillRect(x+10,150,20,90);
    }
    g.generateTexture('foretrees',460,240);
    g.clear();

    // ground strip
    g.fillStyle(0x6b4f2a,1);
    g.fillRect(0,0,128,70);
    g.fillStyle(0x2fae52,1);
    g.fillRect(0,0,128,16);
    g.generateTexture('groundtex',128,70);
    g.destroy();
  }

  buildParallax(){
    const w = this.worldW + 2400;
    this.add.tileSprite(-1200,0,w,WORLD_H,'sky').setOrigin(0,0).setScrollFactor(0);
    this.add.tileSprite(-1200,240,w,260,'hills').setOrigin(0,0).setScrollFactor(0.15);
    this.add.tileSprite(-1200,280,w,220,'midtrees').setOrigin(0,0).setScrollFactor(0.4);
    this.add.tileSprite(-1200,300,w,240,'foretrees').setOrigin(0,0).setScrollFactor(0.75);
  }

  buildGround(){
    const w = this.worldW;
    this.add.tileSprite(0,GROUND_Y,w,70,'groundtex').setOrigin(0,0);
    const rect = this.add.rectangle(w/2, GROUND_Y+35, w, 70, 0x000000, 0);
    this.physics.add.existing(rect, true);
    this.groundBody = rect;
  }

  spawnRocks(cfg){
    const usableW = this.worldW - 500;
    const step = usableW / cfg.rockCount;
    const foodSlots = new Set();
    while(foodSlots.size < Math.min(cfg.foodGoal + 1, cfg.rockCount)){
      foodSlots.add(Phaser.Math.Between(0, cfg.rockCount-1));
    }
    for(let i=0;i<cfg.rockCount;i++){
      const x = 300 + step*i + Phaser.Math.Between(-40,40);
      const hp = cfg.rockHp + Phaser.Math.Between(0, Math.max(1, Math.floor(this.level/12)));
      const kind = Phaser.Utils.Array.GetRandom(ROCK_KINDS);
      const rock = this.add.text(x, GROUND_Y - 8, kind, {fontSize:'46px'}).setOrigin(0.5,1);
      this.physics.add.existing(rock);
      rock.body.setImmovable(true); rock.body.setAllowGravity(false);
      rock.body.setSize(38,40).setOffset(-19,-38);
      rock.hp = hp; rock.maxHp = hp;
      rock.food = foodSlots.has(i) ? Phaser.Utils.Array.GetRandom(FOODS) : null;
      rock.hpLabel = this.add.text(x, GROUND_Y - 56, `${hp}`, {fontSize:'13px', color:'#132015', fontStyle:'bold', backgroundColor:'#ffffffcc', padding:{x:4,y:1}}).setOrigin(0.5);
      this.physics.add.collider(this.player, rock);
      this.rocks.push(rock);
    }
  }

  spawnEnemies(cfg){
    const usableW = this.worldW - 700;
    const step = usableW / Math.max(1,cfg.cavemenCount);
    for(let i=0;i<cfg.cavemenCount;i++){
      const x = 500 + step*i + Phaser.Math.Between(-50,50);
      const hp = 10 + Math.floor(this.level/4);
      const e = this.add.text(x, GROUND_Y - 8, '🧔', {fontSize:'40px'}).setOrigin(0.5,1);
      this.physics.add.existing(e);
      e.body.setSize(30,40).setOffset(-15,-38);
      e.body.setCollideWorldBounds(true);
      e.hp = hp; e.maxHp = hp; e.isEnemy = true; e.enemyType = 'caveman'; e.atkCd = 0;
      e.homeX = x; e.patrolDir = 1;
      this.physics.add.collider(e, this.groundBody);
      for(const r of this.rocks) this.physics.add.collider(e, r);
      this.enemies.push(e);
    }
  }

  bindTouchControls(){
    const bind = (id, onDown, onUp) => {
      const el = document.getElementById(id);
      const down = (ev)=>{ ev.preventDefault(); onDown(); };
      const up = (ev)=>{ ev.preventDefault(); if(onUp) onUp(); };
      el.addEventListener('touchstart', down, {passive:false});
      el.addEventListener('mousedown', down);
      el.addEventListener('touchend', up, {passive:false});
      el.addEventListener('mouseup', up);
      el.addEventListener('mouseleave', up);
    };
    this.touch = {left:false,right:false};
    bind('btn-left', ()=>this.touch.left=true, ()=>this.touch.left=false);
    bind('btn-right', ()=>this.touch.right=true, ()=>this.touch.right=false);
    bind('btn-jump', ()=>this.doJump());
    bind('btn-attack', ()=>this.doAttack());
    bind('btn-roar', ()=>this.doRoar());
  }

  tickTime(){
    if (this.gameOver) return;
    this.timeLeft -= 1;
    const el = document.getElementById('time-count');
    el.textContent = `⏱ ${Math.max(0,this.timeLeft)}s`;
    el.classList.toggle('low', this.timeLeft <= 10);
    if (this.timeLeft <= 0){
      this.endLevel(false, "Out of time! Try grabbing the closest rocks first next run.");
    }
  }

  refreshHud(){
    const p = this.player;
    document.getElementById('dino-fill').style.width = `${Phaser.Math.Clamp(p.dinoHp/p.dinoMaxHp,0,1)*100}%`;
    if (this.ninja){
      document.getElementById('ninja-fill').style.width = `${Phaser.Math.Clamp(this.ninja.hp/this.ninja.maxHp,0,1)*100}%`;
    } else {
      document.getElementById('ninja-fill').style.width = `0%`;
    }
    if (this.boss){
      document.getElementById('boss-row').classList.remove('hidden');
      document.getElementById('boss-fill').style.width = `${Phaser.Math.Clamp(this.boss.hp/this.boss.maxHp,0,1)*100}%`;
    }
  }

  popText(x,y,str,color='#ffffff'){
    const t = this.add.text(x,y,str,{fontSize:'16px', color, fontStyle:'bold', stroke:'#000', strokeThickness:3}).setOrigin(0.5);
    this.tweens.add({targets:t, y:y-36, alpha:0, duration:700, onComplete:()=>t.destroy()});
  }

  nearestTarget(range){
    const px = this.player.x + this.facing*30;
    const py = this.player.y - 20;
    let best = null, bestD = range;
    for(const r of this.rocks){
      if (r.hp<=0) continue;
      const d = Phaser.Math.Distance.Between(px,py,r.x,r.y-20);
      if (d < bestD){ bestD=d; best = {type:'rock', obj:r}; }
    }
    for(const e of this.enemies){
      if (e.hp<=0) continue;
      const d = Phaser.Math.Distance.Between(px,py,e.x,e.y-20);
      if (d < bestD){ bestD=d; best = {type:'enemy', obj:e}; }
    }
    return best;
  }

  doAttack(){
    if (this.gameOver || this.attackCooldown > 0) return;
    this.attackCooldown = 0.35;
    const target = this.nearestTarget(70);
    this.tweens.add({targets:this.player, angle: this.facing*14, duration:80, yoyo:true});
    if (!target){ return; }
    if (target.type === 'rock') this.hitRock(target.obj, 4 + Phaser.Math.Between(0,4), '🦖');
    else this.hitEnemy(target.obj, 6 + Phaser.Math.Between(0,6), '🦖');
  }

  doRoar(){
    if (this.gameOver || this.roarCooldown > 0) return;
    this.roarCooldown = 4.5;
    this.cameras.main.shake(180, 0.006);
    let scared = 0;
    for(const e of this.enemies){
      if (e.hp<=0 || e.enemyType!=='caveman') continue;
      if (Math.abs(e.x - this.player.x) < 240){
        e.hp = Math.max(0, e.hp - Phaser.Math.Between(4,8));
        e.body.setVelocityX(e.x < this.player.x ? -180 : 180);
        this.popText(e.x,e.y-40,'😨','#ffe08a');
        scared++;
        if (e.hp<=0) this.killEnemy(e);
      }
    }
    toast(scared ? `📣 Roar scares off ${scared} caveman/cavemen!` : '📣 Roar echoes... nobody was close enough.', 1400);
  }

  doJump(){
    if (this.gameOver) return;
    if (this.player.body.blocked.down || this.player.body.touching.down){
      this.player.body.setVelocityY(-370);
    }
  }

  hitRock(rock, dmg, source){
    rock.hp = Math.max(0, rock.hp - dmg);
    this.popText(rock.x, rock.y-50, `-${dmg}`, '#ffd27a');
    if (rock.hp<=0){
      if (rock.food){
        this.foodFound++;
        document.getElementById('food-count').textContent = `🍖 ${this.foodFound} / ${this.cfg.foodGoal}`;
        this.popText(rock.x, rock.y-70, rock.food, '#8fffb0');
        toast(`${rock.food} Food found under the rock!`, 1200);
      } else {
        this.popText(rock.x, rock.y-70, '💨', '#cccccc');
      }
      rock.hpLabel.destroy();
      rock.body.enable = false;
      this.tweens.add({targets:rock, alpha:0, scale:0.6, duration:220, onComplete:()=>rock.destroy()});
      this.rocks = this.rocks.filter(r=>r!==rock);
      this.checkWin();
    } else {
      rock.hpLabel.setText(`${rock.hp}`);
      rock.hpLabel.x = rock.x;
    }
  }

  hitEnemy(enemy, dmg, source){
    enemy.hp = Math.max(0, enemy.hp - dmg);
    this.popText(enemy.x, enemy.y-56, `-${dmg}`, '#ff9a7a');
    if (enemy.hp<=0){ this.killEnemy(enemy); }
  }

  killEnemy(enemy){
    if (enemy.dead) return;
    enemy.dead = true;
    this.popText(enemy.x, enemy.y-70, enemy.enemyType==='boss' ? '👑💥' : '✅', '#ffe08a');
    enemy.body.enable = false;
    this.tweens.add({targets:enemy, alpha:0, y:enemy.y-10, duration:300, onComplete:()=>enemy.destroy()});
    if (enemy.enemyType==='boss') { toast('👑 Boss defeated!', 1800); this.boss = null; }
    this.checkWin();
  }

  checkWin(){
    const cfg = this.cfg;
    const bossDone = !cfg.isBoss || !this.boss || this.boss.hp<=0;
    if (this.foodFound >= cfg.foodGoal && bossDone && !this.portalReady){
      this.portalReady = true;
      this.tweens.add({targets:this.portal, scale:1.15, yoyo:true, repeat:-1, duration:500});
      toast('🌀 The portal is glowing — head to it to finish the level!', 2200);
    }
  }

  update(time, delta){
    if (this.gameOver) return;
    const dt = delta/1000;
    this.attackCooldown = Math.max(0, this.attackCooldown - dt);
    this.roarCooldown = Math.max(0, this.roarCooldown - dt);

    // ---- player movement ----
    const left = this.cursors.left.isDown || this.keys.A.isDown || this.touch.left;
    const right = this.cursors.right.isDown || this.keys.D.isDown || this.touch.right;
    const speed = 190;
    if (left && !right){ this.player.body.setVelocityX(-speed); this.facing=-1; this.player.setFlipX(true); }
    else if (right && !left){ this.player.body.setVelocityX(speed); this.facing=1; this.player.setFlipX(false); }
    else { this.player.body.setVelocityX(this.player.body.velocity.x*0.8); }

    if (Phaser.Input.Keyboard.JustDown(this.cursors.up) || Phaser.Input.Keyboard.JustDown(this.keys.SPACE)) this.doJump();
    if (Phaser.Input.Keyboard.JustDown(this.keys.Z)) this.doAttack();
    if (Phaser.Input.Keyboard.JustDown(this.keys.X)) this.doRoar();

    // ---- genie floats & occasionally spawns rocks ----
    this.genie.x = Phaser.Math.Clamp(this.player.x + 340, 200, this.worldW-200);
    this.genie.y = this.genieBaseY + Math.sin(time/450)*10;
    if (Math.random() < this.cfg.genieChancePerSec * dt * 60 && this.rocks.length < this.cfg.rockCount + 8){
      this.spawnGenieRock();
    }

    // ---- ninja follow + auto attack ----
    if (this.ninja && this.ninja.hp > 0){
      const targetX = this.player.x - this.facing*55;
      this.ninja.x = Phaser.Math.Linear(this.ninja.x, targetX, 0.08);
      this.ninja.y = GROUND_Y - 10;
      this.ninja.setFlipX(this.facing < 0);
      this.ninja.atkCd -= dt;
      if (this.ninja.atkCd <= 0){
        for(const e of this.enemies){
          if (e.hp<=0) continue;
          if (Phaser.Math.Distance.Between(this.ninja.x,this.ninja.y,e.x,e.y) < 90){
            this.hitEnemy(e, 5 + Phaser.Math.Between(0,5), '🥷');
            this.popText(this.ninja.x, this.ninja.y-60, '⚡','#cfe0ff');
            this.ninja.atkCd = 1.1;
            break;
          }
        }
      }
    }

    // ---- enemies AI ----
    for(const e of this.enemies){
      if (e.hp<=0 || e.dead) continue;
      const d = Phaser.Math.Distance.Between(e.x,e.y,this.player.x,this.player.y);
      const aggro = e.enemyType==='boss' ? 500 : 320;
      e.atkCd -= dt;
      if (d < aggro){
        const dir = this.player.x < e.x ? -1 : 1;
        e.body.setVelocityX(dir * (e.enemyType==='boss' ? 95 : 75));
        e.setFlipX(dir<0);
        if (d < 46 && e.atkCd <= 0){
          const dmg = e.enemyType==='boss' ? Phaser.Math.Between(6,11) : Phaser.Math.Between(3,7);
          this.player.dinoHp = Math.max(0, this.player.dinoHp - dmg);
          this.popText(this.player.x, this.player.y-64, `-${dmg}`, '#ff6b6b');
          this.cameras.main.shake(90,0.004);
          e.atkCd = e.enemyType==='boss' ? 1.0 : 1.3;
        }
      } else {
        e.body.setVelocityX(Phaser.Math.Between(-1,1)*30);
      }
    }

    // ---- portal check ----
    if (this.portalReady && Phaser.Math.Distance.Between(this.player.x,this.player.y,this.portal.x,this.portal.y) < 70){
      this.endLevel(true);
    }

    // ---- lose check ----
    if (this.player.dinoHp <= 0){
      this.endLevel(false, "The T-Rex got too tired. Try the level again!");
    }

    // ---- fall off world safety ----
    if (this.player.y > WORLD_H + 100){
      this.player.dinoHp = 0;
      this.endLevel(false, "The T-Rex tumbled off the trail!");
    }

    this.refreshHud();
  }

  spawnGenieRock(){
    const x = Phaser.Math.Clamp(this.player.x + Phaser.Math.Between(320,520), 200, this.worldW-200);
    const hp = Math.max(3, this.cfg.rockHp - 1);
    const rock = this.add.text(x, GROUND_Y - 8, '🪨✨', {fontSize:'42px'}).setOrigin(0.5,1);
    this.physics.add.existing(rock);
    rock.body.setImmovable(true); rock.body.setAllowGravity(false);
    rock.body.setSize(38,40).setOffset(-19,-38);
    rock.hp = hp; rock.maxHp = hp;
    rock.food = Math.random() < 0.7 ? Phaser.Utils.Array.GetRandom(FOODS) : null;
    rock.hpLabel = this.add.text(x, GROUND_Y - 56, `${hp}`, {fontSize:'13px', color:'#132015', fontStyle:'bold', backgroundColor:'#ffffffcc', padding:{x:4,y:1}}).setOrigin(0.5);
    this.physics.add.collider(this.player, rock);
    for(const e of this.enemies) this.physics.add.collider(e, rock);
    this.rocks.push(rock);
    toast('🧞 The genie poofs a new rock onto the trail!', 1300);
  }

  endLevel(won, loseMsg){
    if (this.gameOver) return;
    this.gameOver = true;
    this.physics.pause();
    if (won){
      STATE.wins++; STATE.xp += 10 + this.level;
      document.getElementById('win-text').textContent = this.cfg.isBoss
        ? "The boss hunter is defeated and the T-Rex found enough food!"
        : "The T-Rex found enough food and calmed down.";
      document.getElementById('win-stats').innerHTML =
        `<span>🏆 Wins: ${STATE.wins}</span><span>💀 Losses: ${STATE.losses}</span><span>✨ XP: ${STATE.xp}</span>`;
      document.getElementById('overlay-win').classList.remove('hidden');
    } else {
      STATE.losses++;
      document.getElementById('lose-text').textContent = loseMsg || "The T-Rex ran out of energy.";
      document.getElementById('overlay-lose').classList.remove('hidden');
    }
  }
}

/* ============================= PHASER GAME BOOT ============================= */
const config = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: 960,
  height: WORLD_H,
  transparent: true,
  physics: { default: 'arcade', arcade: { gravity: { y: 900 }, debug: false } },
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [PlayScene],
};
let game = null;

function startGame(level){
  document.getElementById('overlay-start').classList.add('hidden');
  document.getElementById('overlay-win').classList.add('hidden');
  document.getElementById('overlay-lose').classList.add('hidden');
  document.getElementById('overlay-finish').classList.add('hidden');
  STATE.level = level;
  if (!game){
    game = new Phaser.Game(config);
    game.scene.start('Play', {level});
  } else {
    game.scene.getScene('Play').scene.restart({level});
  }
}

document.getElementById('btn-start').addEventListener('click', ()=> startGame(1));
document.getElementById('btn-retry').addEventListener('click', ()=> startGame(STATE.level));
document.getElementById('btn-restart').addEventListener('click', ()=>{ STATE.wins=0;STATE.losses=0;STATE.xp=0; startGame(1); });
document.getElementById('btn-restart2').addEventListener('click', ()=>{ STATE.wins=0;STATE.losses=0;STATE.xp=0; startGame(1); });
document.getElementById('btn-next').addEventListener('click', ()=>{
  const next = STATE.level + 1;
  if (next > MAX_LEVEL){
    document.getElementById('overlay-win').classList.add('hidden');
    document.getElementById('overlay-finish').classList.remove('hidden');
  } else {
    startGame(next);
  }
});
</script>
</body>
</html>
