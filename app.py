import random
import time
from dataclasses import dataclass

import streamlit as st

st.set_page_config(page_title="Dino Hangry Rocks", page_icon="🦖", layout="wide")

# -----------------------------
# Kid-friendly game configuration
# -----------------------------
MAX_LEVEL = 50
NINJA_UNLOCK_LEVEL = 6
BOSS_LEVEL_INTERVAL = 10

FOODS = ["🍖", "🥩", "🍗", "🥥", "🍉", "🍌", "🍎"]
ROCK_ICONS = ["🪨", "⛰️", "🧱", "💎"]
CRYSTAL_PIECES = ["🔷", "🔹", "💠", "🔸", "🔶", "✨"]


@dataclass
class LevelConfig:
    level: int
    is_boss: bool
    rock_hp: int
    rock_count: int
    food_goal: int
    cavemen: int
    arrows: int
    genie_chance: float
    boss_hp: int
    dino_max_hp: int
    ninja_max_hp: int
    moves: int


def level_config(level: int) -> LevelConfig:
    """Creates a gentle difficulty curve for kids under 12."""
    is_boss = level % BOSS_LEVEL_INTERVAL == 0
    tier = (level - 1) // 10
    rock_hp = 2 + tier + min(5, level // 8)
    rock_count = 3 + min(7, level // 5)
    food_goal = 2 + min(7, level // 7)
    cavemen = 1 + min(6, level // 8)
    arrows = min(6, level // 9)
    genie_chance = min(0.38, 0.08 + level * 0.004)
    boss_hp = 0 if not is_boss else 18 + level * 3
    dino_max_hp = 34 + min(26, level // 2)
    ninja_max_hp = 0 if level < NINJA_UNLOCK_LEVEL else 16 + min(18, level // 3)
    moves = 16 + max(0, 8 - tier) + (4 if is_boss else 0)
    return LevelConfig(level, is_boss, rock_hp, rock_count, food_goal, cavemen, arrows, genie_chance, boss_hp, dino_max_hp, ninja_max_hp, moves)


def init_state():
    defaults = {
        "level": 1,
        "screen": "intro",
        "xp": 0,
        "wins": 0,
        "losses": 0,
        "message": "Welcome to Dino Hangry Rocks!",
        "log": [],
        "mini_started_at": None,
        "mini_sequence": [],
        "mini_progress": [],
        "mini_seconds": 25,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_log(text: str):
    st.session_state.log.insert(0, text)
    st.session_state.log = st.session_state.log[:6]


def clamp_progress(value: float) -> float:
    """Streamlit progress bars must stay between 0.0 and 1.0."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def start_level(level: int):
    cfg = level_config(level)
    rocks = []
    for i in range(cfg.rock_count):
        hidden_food = random.random() < 0.58
        hp = cfg.rock_hp + random.randint(0, max(1, cfg.level // 12))
        rocks.append({
            "name": f"Rock {i + 1}",
            "hp": hp,
            "max_hp": hp,
            "food": random.choice(FOODS) if hidden_food else None,
            "icon": random.choice(ROCK_ICONS),
        })
    st.session_state.rocks = rocks
    st.session_state.food_found = 0
    st.session_state.dino_hp = cfg.dino_max_hp
    st.session_state.ninja_hp = cfg.ninja_max_hp
    st.session_state.moves_left = cfg.moves
    st.session_state.cavemen_left = cfg.cavemen
    st.session_state.boss_hp = cfg.boss_hp
    st.session_state.genie_mischief = 0
    st.session_state.screen = "battle"
    st.session_state.message = f"Level {level}: Break rocks, find food, and calm the T-Rex's hangry-ness!"
    st.session_state.log = []
    add_log("🧞 The genie hides food under the rocks.")
    if level == NINJA_UNLOCK_LEVEL:
        add_log("🥷 The ninja helper has joined your team!")


def start_mini_game():
    pieces = CRYSTAL_PIECES[:]
    random.shuffle(pieces)
    st.session_state.mini_sequence = pieces
    st.session_state.mini_progress = []
    st.session_state.mini_started_at = time.time()
    st.session_state.mini_seconds = max(12, 28 - st.session_state.level // 3)
    st.session_state.screen = "mini"
    st.session_state.message = "Crystal Puzzle! Put the pieces back together before time runs out."


def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def apply_enemy_turn(cfg: LevelConfig):
    if st.session_state.cavemen_left <= 0 and not cfg.is_boss:
        return
    damage = random.randint(1, 3 + cfg.level // 10)
    if cfg.arrows > 0 and random.random() < 0.35:
        damage += random.randint(1, cfg.arrows)
        add_log("🏹 A caveman throws a stick-arrow!")
    if st.session_state.get("ninja_hp", 0) > 0 and random.random() < 0.45:
        st.session_state.ninja_hp = max(0, st.session_state.ninja_hp - damage)
        add_log(f"🥷 Ninja blocks the attack but takes {damage} damage.")
    else:
        st.session_state.dino_hp = max(0, st.session_state.dino_hp - damage)
        add_log(f"🦖 T-Rex takes {damage} damage.")

    if random.random() < cfg.genie_chance:
        hp = max(2, cfg.rock_hp - 1)
        st.session_state.rocks.append({"name": "Genie Rock", "hp": hp, "max_hp": hp, "food": random.choice(FOODS), "icon": "🧞‍♂️🪨"})
        st.session_state.genie_mischief += 1
        add_log("🧞 The genie poofs a new rock into the path!")


def check_level_end(cfg: LevelConfig):
    if st.session_state.dino_hp <= 0:
        st.session_state.losses += 1
        st.session_state.screen = "lost"
        st.session_state.message = "Oh no! The T-Rex got too tired and lost the level."
        return
    if st.session_state.moves_left <= 0:
        st.session_state.losses += 1
        st.session_state.screen = "lost"
        st.session_state.message = "Out of moves! Try the level again with a better strategy."
        return
    rocks_cleared = all(r["hp"] <= 0 for r in st.session_state.rocks)
    boss_defeated = not cfg.is_boss or st.session_state.boss_hp <= 0
    food_ready = st.session_state.food_found >= cfg.food_goal
    cavemen_clear = st.session_state.cavemen_left <= 0 or not cfg.is_boss
    if food_ready and boss_defeated and (rocks_cleared or cfg.is_boss) and cavemen_clear:
        st.session_state.wins += 1
        st.session_state.xp += 10 + cfg.level
        st.session_state.screen = "won"
        st.session_state.message = f"Level {cfg.level} cleared! The T-Rex found enough food and is less hangry."


def stomp_rock(index: int):
    cfg = level_config(st.session_state.level)
    if index >= len(st.session_state.rocks):
        return
    rock = st.session_state.rocks[index]
    if rock["hp"] <= 0:
        st.session_state.message = "That rock is already broken. Pick another one!"
        return
    hit = random.randint(2, 5 + st.session_state.level // 12)
    rock["hp"] = max(0, rock["hp"] - hit)
    st.session_state.moves_left -= 1
    add_log(f"🦖 T-Rex stomps {rock['name']} for {hit} damage.")
    if rock["hp"] == 0:
        if rock.get("food"):
            st.session_state.food_found += 1
            add_log(f"{rock['food']} Food found under {rock['name']}!")
        else:
            add_log("Dust everywhere, but no snack under this one.")
    apply_enemy_turn(cfg)
    check_level_end(cfg)


def ninja_strike():
    cfg = level_config(st.session_state.level)
    if st.session_state.level < NINJA_UNLOCK_LEVEL:
        st.session_state.message = "The ninja unlocks at Level 6."
        return
    if st.session_state.ninja_hp <= 0:
        st.session_state.message = "The ninja is knocked out for this level."
        return
    active_rocks = [i for i, r in enumerate(st.session_state.rocks) if r["hp"] > 0]
    if not active_rocks:
        st.session_state.message = "No rocks left for the ninja to strike."
        return
    idx = random.choice(active_rocks)
    rock = st.session_state.rocks[idx]
    hit = random.randint(3, 6 + st.session_state.level // 10)
    rock["hp"] = max(0, rock["hp"] - hit)
    st.session_state.moves_left -= 1
    add_log(f"🥷 Ninja slices {rock['name']} for {hit} damage.")
    if rock["hp"] == 0 and rock.get("food"):
        st.session_state.food_found += 1
        add_log(f"{rock['food']} Ninja uncovered food!")
    apply_enemy_turn(cfg)
    check_level_end(cfg)


def roar_scare():
    cfg = level_config(st.session_state.level)
    st.session_state.moves_left -= 1
    scared = random.randint(0, 2 + st.session_state.level // 15)
    if scared > 0:
        st.session_state.cavemen_left = max(0, st.session_state.cavemen_left - scared)
        add_log(f"📣 T-Rex roars and scares away {scared} caveman/cavemen!")
    else:
        add_log("📣 T-Rex roars, but the cavemen hold steady.")
    apply_enemy_turn(cfg)
    check_level_end(cfg)


def boss_attack():
    cfg = level_config(st.session_state.level)
    if not cfg.is_boss:
        return
    damage = random.randint(5, 9 + st.session_state.level // 10)
    st.session_state.boss_hp = max(0, st.session_state.boss_hp - damage)
    st.session_state.moves_left -= 1
    add_log(f"⚔️ Team attack hits the mighty hunter for {damage} damage!")
    if random.random() < 0.4:
        st.session_state.cavemen_left = max(0, st.session_state.cavemen_left - 1)
        add_log("A mob helper runs away from the battle!")
    apply_enemy_turn(cfg)
    check_level_end(cfg)


def render_css():
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(135deg, #101820 0%, #1b4332 50%, #081c15 100%); color: #f7fff7; }
        section[data-testid="stSidebar"] { background: #081c15; }
        .game-card { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); border-radius: 18px; padding: 18px; margin: 8px 0; box-shadow: 0 8px 24px rgba(0,0,0,0.22); }
        .hero-title { font-size: 48px; font-weight: 900; line-height: 1.05; }
        .big-emoji { font-size: 78px; text-align:center; }
        .stat-pill { display:inline-block; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.13); margin:4px; border:1px solid rgba(255,255,255,.18); }
        .small-note { opacity:.85; font-size:14px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.title("🦖 Dino Controls")
    st.sidebar.write(f"**Level:** {st.session_state.level}/{MAX_LEVEL}")
    st.sidebar.write(f"**Wins:** {st.session_state.wins}  |  **Tries lost:** {st.session_state.losses}")
    st.sidebar.write(f"**XP:** {st.session_state.xp}")
    st.sidebar.progress(st.session_state.level / MAX_LEVEL)
    if st.sidebar.button("Start / Restart Current Level", use_container_width=True):
        start_level(st.session_state.level)
        st.rerun()
    if st.sidebar.button("New Game", use_container_width=True):
        reset_game()
        st.rerun()
    with st.sidebar.expander("How to play"):
        st.write("Break rocks to find food. Food calms the T-Rex's hangry meter.")
        st.write("The ninja unlocks at Level 6 and can help break rocks.")
        st.write("Every 10th level is a boss fight against mighty cavemen hunters.")
        st.write("Between levels, solve the crystal puzzle by clicking the pieces in the shown order.")


def render_how_to_play_card():
    st.markdown(
        """
        <div class="game-card">
        <h3>🎮 How to Play</h3>
        <b>Controls:</b> Use your <b>mouse, trackpad, or touchscreen</b>. Click the game buttons to choose actions.
        Keyboard arrow keys are not needed in this Streamlit version.<br><br>
        <b>Main goal:</b> Break rocks to find enough food before the T-Rex runs out of HP or moves.<br>
        <b>Stomp this rock:</b> T-Rex attacks one rock.<br>
        <b>Dino Roar:</b> Scares away cavemen. Use this when cavemen are building up.<br>
        <b>Ninja Strike:</b> Unlocks at Level 6 and helps break rocks. The ninja can be knocked out, but the T-Rex must survive.<br>
        <b>Boss Levels:</b> Every 10th level, use rock stomps, roar, ninja strike, and boss attacks to defeat the mighty hunter.<br>
        <b>Crystal Puzzle:</b> Between levels, click the crystal pieces in the exact order shown before time runs out.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_intro():
    st.markdown('<div class="hero-title">Dino Hangry Rocks</div>', unsafe_allow_html=True)
    render_how_to_play_card()
    st.markdown('<div class="game-card">A T-Rex is hangry! Cavemen and a sneaky genie keep hiding food under stronger and stronger rocks. Stomp rocks, find snacks, unlock the ninja helper, and beat boss hunters every 10 levels.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="game-card big-emoji">🦖<br><span class="small-note">T-Rex Hero</span></div>', unsafe_allow_html=True)
    c2.markdown('<div class="game-card big-emoji">🥷<br><span class="small-note">Ninja Helper at Level 6</span></div>', unsafe_allow_html=True)
    c3.markdown('<div class="game-card big-emoji">🧞‍♂️<br><span class="small-note">Mischief Genie</span></div>', unsafe_allow_html=True)
    if st.button("Start Level 1", type="primary", use_container_width=True):
        start_level(1)
        st.rerun()


def render_status(cfg: LevelConfig):
    st.markdown(f"### {st.session_state.message}")
    st.markdown(
        f"<span class='stat-pill'>🦖 Dino HP: {st.session_state.dino_hp}/{cfg.dino_max_hp}</span>"
        f"<span class='stat-pill'>🍖 Food: {st.session_state.food_found}/{cfg.food_goal}</span>"
        f"<span class='stat-pill'>👣 Moves: {st.session_state.moves_left}</span>"
        f"<span class='stat-pill'>🧔 Cavemen: {st.session_state.cavemen_left}</span>"
        f"<span class='stat-pill'>🧞 Genie tricks: {st.session_state.genie_mischief}</span>",
        unsafe_allow_html=True,
    )
    if st.session_state.level >= NINJA_UNLOCK_LEVEL:
        st.markdown(f"<span class='stat-pill'>🥷 Ninja HP: {st.session_state.ninja_hp}/{cfg.ninja_max_hp}</span>", unsafe_allow_html=True)
    if cfg.is_boss:
        st.markdown(f"<span class='stat-pill'>👑 Boss HP: {st.session_state.boss_hp}/{cfg.boss_hp}</span>", unsafe_allow_html=True)
        st.progress(clamp_progress(0 if cfg.boss_hp == 0 else st.session_state.boss_hp / cfg.boss_hp))


def render_battle():
    cfg = level_config(st.session_state.level)
    with st.expander("🎮 How to play this level", expanded=True):
        st.write("Use your mouse, trackpad, or touchscreen. Click **Stomp this rock** to break rocks and find food. Click **Dino Roar** to scare cavemen. From Level 6 on, click **Ninja Strike** for extra help. On boss levels, also use **Attack Boss**.")
    render_status(cfg)
    left, right = st.columns([2, 1])
    with left:
        st.markdown("#### Rocks hiding food")
        cols = st.columns(3)
        for i, rock in enumerate(st.session_state.rocks):
            with cols[i % 3]:
                hp_ratio = 0 if rock["max_hp"] == 0 else rock["hp"] / rock["max_hp"]
                st.markdown(f"<div class='game-card'><div style='font-size:42px;text-align:center'>{rock['icon']}</div><b>{rock['name']}</b><br>HP: {rock['hp']}/{rock['max_hp']}</div>", unsafe_allow_html=True)
                st.progress(clamp_progress(hp_ratio))
                disabled = rock["hp"] <= 0
                if st.button("Stomp this rock", key=f"rock_{i}", disabled=disabled, use_container_width=True):
                    stomp_rock(i)
                    st.rerun()
    with right:
        st.markdown("#### Team Actions")
        if st.button("🥷 Ninja Strike", disabled=st.session_state.level < NINJA_UNLOCK_LEVEL or st.session_state.get("ninja_hp", 0) <= 0, use_container_width=True):
            ninja_strike()
            st.rerun()
        if st.button("📣 Dino Roar", use_container_width=True):
            roar_scare()
            st.rerun()
        if cfg.is_boss and st.button("⚔️ Attack Boss", type="primary", use_container_width=True):
            boss_attack()
            st.rerun()
        st.markdown("#### Adventure Log")
        for item in st.session_state.log:
            st.write(item)


def render_won():
    st.success(st.session_state.message)
    st.balloons()
    st.markdown("### Next: Crystal mini-game")
    st.write("Before the next level, put the crystal back together in the correct order.")
    if st.button("Start Crystal Puzzle", type="primary", use_container_width=True):
        start_mini_game()
        st.rerun()


def render_lost():
    st.error(st.session_state.message)
    st.write("Tip: Find food first, use roar when cavemen build up, and save the ninja for tough rocks or boss levels.")
    if st.button("Try Level Again", type="primary", use_container_width=True):
        start_level(st.session_state.level)
        st.rerun()


def render_mini():
    sequence = st.session_state.mini_sequence
    elapsed = int(time.time() - st.session_state.mini_started_at) if st.session_state.mini_started_at else 0
    remaining = max(0, st.session_state.mini_seconds - elapsed)
    st.markdown("## 💎 Crystal Puzzle")
    with st.expander("🎮 Crystal puzzle controls", expanded=True):
        st.write("Use your mouse, trackpad, or touchscreen. Look at the order shown below, then click the crystal buttons in that same order before time runs out.")
    st.write("Click the crystal pieces in this exact order before time runs out:")
    st.markdown("### " + "  ".join(sequence))
    st.progress(clamp_progress(remaining / st.session_state.mini_seconds))
    st.write(f"Time left: **{remaining} seconds**")
    if remaining <= 0:
        st.warning("Time ran out! You can still continue, but the next level starts with fewer bonus moves.")
    st.write("Your crystal so far: " + " ".join(st.session_state.mini_progress))
    cols = st.columns(6)
    shuffled = sequence[:]
    random.seed(st.session_state.level)
    random.shuffle(shuffled)
    for i, piece in enumerate(shuffled):
        with cols[i % 6]:
            if st.button(piece, key=f"piece_{i}_{piece}", use_container_width=True):
                target_index = len(st.session_state.mini_progress)
                if target_index < len(sequence) and piece == sequence[target_index]:
                    st.session_state.mini_progress.append(piece)
                    st.session_state.message = "Correct crystal piece!"
                    if len(st.session_state.mini_progress) == len(sequence):
                        st.session_state.xp += 5
                        next_level = st.session_state.level + 1
                        if next_level > MAX_LEVEL:
                            st.session_state.screen = "complete"
                        else:
                            st.session_state.level = next_level
                            start_level(next_level)
                    st.rerun()
                else:
                    st.session_state.mini_progress = []
                    st.session_state.message = "Oops! Wrong piece. The crystal resets. Try again!"
                    st.rerun()
    st.info(st.session_state.message)
    if st.button("Skip puzzle and continue", use_container_width=True):
        next_level = st.session_state.level + 1
        if next_level > MAX_LEVEL:
            st.session_state.screen = "complete"
        else:
            st.session_state.level = next_level
            start_level(next_level)
        st.rerun()


def render_complete():
    st.balloons()
    st.markdown("# 🏆 You beat all 50 starter levels!")
    st.write("The T-Rex is full, the ninja is proud, and the genie needs a nap.")
    if st.button("Play Again", type="primary"):
        reset_game()
        st.rerun()


def render_level_map():
    st.markdown("### Level Roadmap")
    rows = []
    for lvl in range(1, MAX_LEVEL + 1):
        if lvl % 10 == 0:
            label = "👑 Boss"
        elif lvl == NINJA_UNLOCK_LEVEL:
            label = "🥷 Ninja Unlock"
        elif lvl < 10:
            label = "🪨 Easy Rocks"
        elif lvl < 25:
            label = "⛰️ Tougher Rocks"
        elif lvl < 40:
            label = "🧞 More Genie Tricks"
        else:
            label = "🔥 Final Challenge"
        rows.append({"Level": lvl, "Type": label})
    st.dataframe(rows, use_container_width=True, hide_index=True)


def main():
    init_state()
    render_css()
    render_sidebar()
    tab1, tab2 = st.tabs(["Game", "50-Level Plan"])
    with tab1:
        screen = st.session_state.screen
        if screen == "intro":
            render_intro()
        elif screen == "battle":
            render_battle()
        elif screen == "won":
            render_won()
        elif screen == "lost":
            render_lost()
        elif screen == "mini":
            render_mini()
        elif screen == "complete":
            render_complete()
    with tab2:
        render_level_map()
        st.markdown("#### Future upgrades")
        st.write("Add moving sprites, sound effects, collectible dinosaur skins, stronger crystal puzzles, and custom level art later.")


if __name__ == "__main__":
    main()
