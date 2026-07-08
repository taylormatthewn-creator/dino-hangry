import random
import time
from dataclasses import dataclass

import streamlit as st

st.set_page_config(page_title="Dino Hangry Rocks", page_icon="🦖", layout="wide")

MAX_LEVEL = 50
NINJA_UNLOCK_LEVEL = 6
BOSS_INTERVAL = 10
DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}
FOODS = ["🍖", "🥩", "🍗", "🍉", "🍌", "🥥"]
CRYSTAL_PIECES = ["🔷", "🔹", "💠", "🔸", "🔶", "✨"]


@dataclass
class LevelConfig:
    level: int
    board_size: int
    rock_count: int
    rock_hp: int
    food_goal: int
    cavemen: int
    dino_hp: int
    ninja_hp: int
    moves: int
    genie_chance: float
    boss_hp: int
    is_boss: bool


def cfg_for(level: int) -> LevelConfig:
    tier = (level - 1) // 10
    is_boss = level % BOSS_INTERVAL == 0
    return LevelConfig(
        level=level,
        board_size=7 if level < 16 else 8 if level < 36 else 9,
        rock_count=5 + min(11, level // 3),
        rock_hp=3 + tier + min(6, level // 8),
        food_goal=2 + min(6, level // 8),
        cavemen=1 + min(8, level // 6) + (3 if is_boss else 0),
        dino_hp=38 + min(28, level // 2),
        ninja_hp=0 if level < NINJA_UNLOCK_LEVEL else 18 + min(25, level // 3),
        moves=28 + max(0, 10 - tier) + (8 if is_boss else 0),
        genie_chance=min(0.34, 0.07 + level * 0.004),
        boss_hp=0 if not is_boss else 28 + level * 3,
        is_boss=is_boss,
    )


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def empty_cells(board_size: int):
    return [(r, c) for r in range(board_size) for c in range(board_size)]


def manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def random_cell(open_cells):
    cell = random.choice(open_cells)
    open_cells.remove(cell)
    return cell


def add_log(text: str):
    st.session_state.log.insert(0, text)
    st.session_state.log = st.session_state.log[:10]


def init_state():
    defaults = {
        "screen": "intro",
        "level": 1,
        "wins": 0,
        "losses": 0,
        "xp": 0,
        "log": [],
        "message": "Welcome to Dino Hangry Rocks!",
        "mini_sequence": [],
        "mini_progress": [],
        "mini_started": None,
        "mini_seconds": 28,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def start_level(level: int):
    cfg = cfg_for(level)
    open_cells = empty_cells(cfg.board_size)
    dino_pos = (cfg.board_size - 1, cfg.board_size // 2)
    open_cells.remove(dino_pos)
    genie_pos = (0, cfg.board_size // 2)
    if genie_pos in open_cells:
        open_cells.remove(genie_pos)

    rocks = {}
    food_positions = set(random.sample(range(cfg.rock_count), min(cfg.food_goal + 1, cfg.rock_count)))
    for i in range(cfg.rock_count):
        pos = random_cell(open_cells)
        hp = cfg.rock_hp + random.randint(0, max(1, level // 15))
        rocks[pos] = {
            "hp": hp,
            "max_hp": hp,
            "food": random.choice(FOODS) if i in food_positions else None,
            "kind": random.choice(["🪨", "⛰️", "🧱"]),
        }

    enemies = []
    for i in range(cfg.cavemen):
        if not open_cells:
            break
        enemies.append({"type": "caveman", "pos": random_cell(open_cells), "hp": 8 + level // 5, "max_hp": 8 + level // 5})
    if cfg.is_boss and open_cells:
        enemies.append({"type": "boss", "pos": random_cell(open_cells), "hp": cfg.boss_hp, "max_hp": cfg.boss_hp})

    st.session_state.board_size = cfg.board_size
    st.session_state.dino_pos = dino_pos
    st.session_state.ninja_pos = None if level < NINJA_UNLOCK_LEVEL else (cfg.board_size - 1, max(0, cfg.board_size // 2 - 1))
    st.session_state.genie_pos = genie_pos
    st.session_state.rocks = rocks
    st.session_state.enemies = enemies
    st.session_state.food_found = 0
    st.session_state.dino_hp = cfg.dino_hp
    st.session_state.dino_max_hp = cfg.dino_hp
    st.session_state.ninja_hp = cfg.ninja_hp
    st.session_state.ninja_max_hp = cfg.ninja_hp
    st.session_state.moves_left = cfg.moves
    st.session_state.genie_mischief = 0
    st.session_state.screen = "play"
    st.session_state.log = []
    st.session_state.message = f"Level {level}: Move the T-Rex through the forest, smash rocks, and find food!"
    add_log("🧞 The genie hid food under rocks around the forest.")
    if level == NINJA_UNLOCK_LEVEL:
        add_log("🥷 The ninja helper has joined your team!")
    if cfg.is_boss:
        add_log("👑 Boss level! Defeat the mighty caveman hunter.")


def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def in_bounds(pos):
    size = st.session_state.board_size
    return 0 <= pos[0] < size and 0 <= pos[1] < size


def enemy_at(pos):
    for idx, enemy in enumerate(st.session_state.enemies):
        if enemy["pos"] == pos and enemy["hp"] > 0:
            return idx, enemy
    return None, None


def rock_at(pos):
    rock = st.session_state.rocks.get(pos)
    if rock and rock["hp"] > 0:
        return rock
    return None


def uncover_food(rock, pos):
    if rock.get("food"):
        st.session_state.food_found += 1
        add_log(f"{rock['food']} Food found under the rock!")
        rock["food"] = None
    else:
        add_log("Dust cloud! No snack under that rock.")
    st.session_state.rocks.pop(pos, None)


def stomp_position(pos, power_bonus=0, source="🦖 T-Rex"):
    rock = rock_at(pos)
    if not rock:
        return False
    damage = random.randint(3, 6 + st.session_state.level // 10) + power_bonus
    rock["hp"] = max(0, rock["hp"] - damage)
    add_log(f"{source} smashes a rock for {damage} damage.")
    if rock["hp"] <= 0:
        uncover_food(rock, pos)
    return True


def attack_enemy(pos, power_bonus=0, source="🦖 T-Rex"):
    idx, enemy = enemy_at(pos)
    if enemy is None:
        return False
    damage = random.randint(5, 10 + st.session_state.level // 10) + power_bonus
    enemy["hp"] = max(0, enemy["hp"] - damage)
    label = "boss hunter" if enemy["type"] == "boss" else "caveman"
    add_log(f"{source} hits the {label} for {damage} damage.")
    if enemy["hp"] <= 0:
        add_log(f"✅ The {label} is defeated!")
    return True


def move_dino(direction: str):
    if st.session_state.screen != "play":
        return
    dr, dc = DIRECTIONS[direction]
    current = st.session_state.dino_pos
    target = (current[0] + dr, current[1] + dc)
    if not in_bounds(target):
        st.session_state.message = "The forest is too thick that way. Choose another direction."
        return

    st.session_state.moves_left -= 1
    if stomp_position(target):
        pass
    elif attack_enemy(target):
        pass
    else:
        st.session_state.dino_pos = target
        add_log("🦖 T-Rex stomps through the forest.")
    helper_auto_turn()
    enemy_turn()
    check_end()


def roar():
    st.session_state.moves_left -= 1
    dino = st.session_state.dino_pos
    scared = 0
    for enemy in st.session_state.enemies:
        if enemy["hp"] > 0 and enemy["type"] == "caveman" and manhattan(dino, enemy["pos"]) <= 2:
            enemy["hp"] = max(0, enemy["hp"] - random.randint(4, 7))
            scared += 1
    if scared:
        add_log(f"📣 Dino Roar scares {scared} nearby caveman/cavemen!")
    else:
        add_log("📣 Dino Roar echoes through the forest, but no cavemen were close.")
    enemy_turn()
    check_end()


def ninja_special():
    if st.session_state.level < NINJA_UNLOCK_LEVEL:
        st.session_state.message = "The ninja helper unlocks at Level 6."
        return
    if st.session_state.ninja_hp <= 0:
        st.session_state.message = "The ninja is knocked out for this level, but the T-Rex can still win."
        return
    st.session_state.moves_left -= 1
    dino = st.session_state.dino_pos
    targets = []
    for pos, rock in st.session_state.rocks.items():
        if rock["hp"] > 0 and manhattan(dino, pos) <= 2:
            targets.append(("rock", pos))
    for enemy in st.session_state.enemies:
        if enemy["hp"] > 0 and manhattan(dino, enemy["pos"]) <= 2:
            targets.append(("enemy", enemy["pos"]))
    if not targets:
        add_log("🥷 Ninja flips forward, but nothing is close enough to hit.")
    else:
        kind, pos = random.choice(targets)
        if kind == "rock":
            stomp_position(pos, power_bonus=3, source="🥷 Ninja")
        else:
            attack_enemy(pos, power_bonus=4, source="🥷 Ninja")
    enemy_turn()
    check_end()


def helper_auto_turn():
    if st.session_state.level < NINJA_UNLOCK_LEVEL or st.session_state.ninja_hp <= 0:
        return
    dino = st.session_state.dino_pos
    st.session_state.ninja_pos = (dino[0], max(0, dino[1] - 1))
    nearby_enemies = [e["pos"] for e in st.session_state.enemies if e["hp"] > 0 and manhattan(dino, e["pos"]) <= 1]
    if nearby_enemies and random.random() < 0.5:
        attack_enemy(random.choice(nearby_enemies), power_bonus=2, source="🥷 Ninja auto-help")


def step_toward(start, target):
    sr, sc = start
    tr, tc = target
    options = []
    if sr < tr:
        options.append((sr + 1, sc))
    if sr > tr:
        options.append((sr - 1, sc))
    if sc < tc:
        options.append((sr, sc + 1))
    if sc > tc:
        options.append((sr, sc - 1))
    random.shuffle(options)
    blocked = set(st.session_state.rocks.keys()) | {st.session_state.dino_pos}
    for option in options:
        if in_bounds(option) and option not in blocked:
            return option
    return start


def enemy_turn():
    if st.session_state.screen != "play":
        return
    dino = st.session_state.dino_pos
    ninja_alive = st.session_state.level >= NINJA_UNLOCK_LEVEL and st.session_state.ninja_hp > 0
    for enemy in st.session_state.enemies:
        if enemy["hp"] <= 0:
            continue
        distance = manhattan(enemy["pos"], dino)
        if distance <= 1:
            damage = random.randint(2, 5 if enemy["type"] == "caveman" else 8)
            if ninja_alive and random.random() < 0.45:
                st.session_state.ninja_hp = max(0, st.session_state.ninja_hp - damage)
                add_log(f"🥷 Ninja blocks an attack and takes {damage} damage.")
                ninja_alive = st.session_state.ninja_hp > 0
            else:
                st.session_state.dino_hp = max(0, st.session_state.dino_hp - damage)
                add_log(f"🏹 Caveman attack! T-Rex takes {damage} damage.")
        elif random.random() < 0.45:
            enemy["pos"] = step_toward(enemy["pos"], dino)

    cfg = cfg_for(st.session_state.level)
    if random.random() < cfg.genie_chance:
        spawn_genie_rock()


def spawn_genie_rock():
    size = st.session_state.board_size
    occupied = {st.session_state.dino_pos, st.session_state.genie_pos}
    occupied |= {pos for pos, r in st.session_state.rocks.items() if r["hp"] > 0}
    occupied |= {e["pos"] for e in st.session_state.enemies if e["hp"] > 0}
    open_cells = [pos for pos in empty_cells(size) if pos not in occupied and manhattan(pos, st.session_state.dino_pos) > 1]
    if not open_cells:
        return
    pos = random.choice(open_cells)
    hp = max(2, cfg_for(st.session_state.level).rock_hp - 1)
    st.session_state.rocks[pos] = {"hp": hp, "max_hp": hp, "food": random.choice(FOODS) if random.random() < 0.7 else None, "kind": "🧞‍♂️🪨"}
    st.session_state.genie_mischief += 1
    add_log("🧞 Genie poofs a new rock into the forest!")


def check_end():
    cfg = cfg_for(st.session_state.level)
    boss_alive = any(e["type"] == "boss" and e["hp"] > 0 for e in st.session_state.enemies)
    if st.session_state.dino_hp <= 0:
        st.session_state.losses += 1
        st.session_state.screen = "lost"
        st.session_state.message = "Oh no! The T-Rex got too tired. Try the level again."
        return
    if st.session_state.moves_left <= 0:
        st.session_state.losses += 1
        st.session_state.screen = "lost"
        st.session_state.message = "Out of moves! Try again and choose the closest rocks first."
        return
    if st.session_state.food_found >= cfg.food_goal and (not cfg.is_boss or not boss_alive):
        st.session_state.wins += 1
        st.session_state.xp += 10 + st.session_state.level
        st.session_state.screen = "won"
        st.session_state.message = "Level cleared! The T-Rex found enough food and calmed down."


def start_mini_game():
    pieces = CRYSTAL_PIECES[:]
    random.shuffle(pieces)
    st.session_state.mini_sequence = pieces
    st.session_state.mini_progress = []
    st.session_state.mini_started = time.time()
    st.session_state.mini_seconds = max(14, 30 - st.session_state.level // 3)
    st.session_state.screen = "mini"
    st.session_state.message = "Crystal Puzzle: click the pieces in the correct order before time runs out!"


def mini_click(piece):
    expected = st.session_state.mini_sequence[len(st.session_state.mini_progress)]
    if piece == expected:
        st.session_state.mini_progress.append(piece)
        if len(st.session_state.mini_progress) == len(st.session_state.mini_sequence):
            st.session_state.xp += 5
            next_level()
    else:
        st.session_state.mini_progress = []
        st.session_state.message = "Oops! Wrong crystal piece. Try the sequence again."


def next_level():
    if st.session_state.level >= MAX_LEVEL:
        st.session_state.screen = "finished"
        st.session_state.message = "You beat all 50 starter levels!"
    else:
        st.session_state.level += 1
        start_level(st.session_state.level)


def cell_html(r, c):
    """Return one board tile as compact HTML.

    Important: do not indent the returned HTML. Markdown treats 4 leading
    spaces as a code block, which caused the forest grid to show raw HTML on
    Streamlit Cloud.
    """
    pos = (r, c)
    contents = []
    title = "Forest"
    tile_class = "terrain"

    if pos == st.session_state.genie_pos:
        contents.append("🧞")
        title = "Genie Cave"
        tile_class = "genie"

    rock = rock_at(pos)
    if rock:
        contents.append(rock["kind"])
        title = f"Rock HP {rock['hp']}/{rock['max_hp']}"
        tile_class = "rock"

    for enemy in st.session_state.enemies:
        if enemy["pos"] == pos and enemy["hp"] > 0:
            if enemy["type"] == "boss":
                contents.append("👑🧔")
                title = f"Boss HP {enemy['hp']}/{enemy['max_hp']}"
                tile_class = "boss"
            else:
                contents.append("🧔")
                title = f"Caveman HP {enemy['hp']}/{enemy['max_hp']}"
                tile_class = "enemy"

    if st.session_state.ninja_pos == pos and st.session_state.ninja_hp > 0:
        contents.append("🥷")
        title = "Ninja Helper"
        tile_class = "ninja"

    if st.session_state.dino_pos == pos:
        contents.append("🦖")
        title = "T-Rex"
        tile_class = "dino"

    if not contents:
        # Stable decoration based on position so the board does not flicker.
        forest = ["🌲", "🌳", "🌿", "🍃"]
        contents.append(forest[(r * 3 + c * 5 + st.session_state.level) % len(forest)])

    label = " ".join(contents)
    return f"<div class='forest-cell {tile_class}' title='{title}'><div class='cell-emoji'>{label}</div><div class='cell-label'>{title}</div></div>"


def render_board():
    size = st.session_state.board_size
    grid = "<div class='forest-grid' style='grid-template-columns: repeat(%s, 1fr);'>" % size
    for r in range(size):
        for c in range(size):
            grid += cell_html(r, c)
    grid += "</div>"
    st.markdown(grid, unsafe_allow_html=True)


def render_stats():
    cfg = cfg_for(st.session_state.level)
    enemies_alive = sum(1 for e in st.session_state.enemies if e["hp"] > 0)
    boss = next((e for e in st.session_state.enemies if e["type"] == "boss"), None)
    st.markdown(
        f"""
        <div class='hud'>
          <span>🦖 Dino HP: {st.session_state.dino_hp}/{st.session_state.dino_max_hp}</span>
          <span>🍖 Food: {st.session_state.food_found}/{cfg.food_goal}</span>
          <span>👣 Moves: {st.session_state.moves_left}</span>
          <span>🧔 Enemies: {enemies_alive}</span>
          <span>🧞 Genie rocks: {st.session_state.genie_mischief}</span>
          <span>🥷 Ninja: {'Locked' if st.session_state.level < NINJA_UNLOCK_LEVEL else str(st.session_state.ninja_hp) + '/' + str(st.session_state.ninja_max_hp)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(clamp(st.session_state.dino_hp / max(1, st.session_state.dino_max_hp)), text="Dino energy")
    if st.session_state.level >= NINJA_UNLOCK_LEVEL:
        st.progress(clamp(st.session_state.ninja_hp / max(1, st.session_state.ninja_max_hp)), text="Ninja energy")
    if boss:
        st.progress(clamp(boss["hp"] / max(1, boss["max_hp"])), text="Boss health")


def render_controls():
    st.subheader("🎮 Controls")
    st.caption("Use the buttons like a controller. Move into a rock to smash it. Move into a caveman or boss to attack. Keyboard arrows are not required in Streamlit.")
    top = st.columns([1, 1, 1])
    with top[1]:
        if st.button("⬆️ Up", use_container_width=True):
            move_dino("up")
            st.rerun()
    mid = st.columns([1, 1, 1])
    with mid[0]:
        if st.button("⬅️ Left", use_container_width=True):
            move_dino("left")
            st.rerun()
    with mid[1]:
        if st.button("📣 Dino Roar", use_container_width=True):
            roar()
            st.rerun()
    with mid[2]:
        if st.button("➡️ Right", use_container_width=True):
            move_dino("right")
            st.rerun()
    bottom = st.columns([1, 1, 1])
    with bottom[1]:
        if st.button("⬇️ Down", use_container_width=True):
            move_dino("down")
            st.rerun()
    if st.session_state.level >= NINJA_UNLOCK_LEVEL:
        if st.button("🥷 Ninja Special", use_container_width=True, disabled=st.session_state.ninja_hp <= 0):
            ninja_special()
            st.rerun()


def render_log():
    st.subheader("Adventure Log")
    for item in st.session_state.log:
        st.markdown(f"<div class='log-item'>{item}</div>", unsafe_allow_html=True)


def render_play():
    st.markdown(f"## Level {st.session_state.level}: Forest Rock Smash")
    st.info(st.session_state.message)
    render_stats()
    left, right = st.columns([2.2, 1])
    with left:
        render_board()
    with right:
        render_controls()
        render_log()


def render_intro():
    st.markdown("# 🦖 Dino Hangry Rocks")
    st.markdown(
        """
        <div class='story-card'>
        A hungry T-Rex is stomping through the forest looking for food. The problem: a mischievous genie keeps hiding snacks under rocks and helping the cavemen block the way.
        <br><br>
        Your mission is to move the T-Rex around the forest, smash rocks, find enough food, avoid getting knocked out, and beat boss hunters every 10 levels.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### How to play")
    st.markdown(
        """
        - Use the **on-screen arrow buttons** with a mouse, trackpad, or touchscreen.
        - Move into a **rock** to smash it.
        - Move into a **caveman** or **boss** to attack.
        - Use **Dino Roar** to scare nearby cavemen.
        - At **Level 6**, the **ninja helper** unlocks.
        - After each level, complete a quick **timed crystal puzzle**.
        """
    )
    if st.button("▶️ Start Adventure", use_container_width=True):
        start_level(st.session_state.level)
        st.rerun()


def render_won():
    st.success(st.session_state.message)
    st.balloons()
    st.markdown("### 💎 Bonus Crystal Puzzle")
    st.write("Before the next level, help the T-Rex put the crystal back together.")
    if st.button("Start Crystal Puzzle", use_container_width=True):
        start_mini_game()
        st.rerun()
    if st.button("Skip puzzle and go to next level", use_container_width=True):
        next_level()
        st.rerun()


def render_lost():
    st.error(st.session_state.message)
    st.write("Try again. Hint: chase the closest rocks first, and use Dino Roar when cavemen get close.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Retry Current Level", use_container_width=True):
            start_level(st.session_state.level)
            st.rerun()
    with c2:
        if st.button("New Game", use_container_width=True):
            reset_game()
            st.rerun()


def render_mini():
    elapsed = int(time.time() - st.session_state.mini_started)
    left = max(0, st.session_state.mini_seconds - elapsed)
    st.markdown("# 💎 Crystal Puzzle")
    st.write("Click the crystal pieces in the exact order shown. If you click the wrong piece, the puzzle resets.")
    st.progress(clamp(left / max(1, st.session_state.mini_seconds)), text=f"Time left: {left} seconds")
    if left <= 0:
        st.warning("Time ran out, but this is kid-friendly. You can retry or continue.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Retry Puzzle", use_container_width=True):
                start_mini_game()
                st.rerun()
        with c2:
            if st.button("Continue to Next Level", use_container_width=True):
                next_level()
                st.rerun()
        return
    st.markdown("### Target order")
    st.markdown(" ".join(st.session_state.mini_sequence))
    st.markdown("### Your progress")
    st.markdown(" ".join(st.session_state.mini_progress) if st.session_state.mini_progress else "_No pieces placed yet._")
    shuffled = st.session_state.mini_sequence[:]
    random.seed(st.session_state.level + len(st.session_state.mini_progress))
    random.shuffle(shuffled)
    cols = st.columns(len(shuffled))
    for col, piece in zip(cols, shuffled):
        with col:
            if st.button(piece, key=f"mini_{piece}_{len(st.session_state.mini_progress)}", use_container_width=True):
                mini_click(piece)
                st.rerun()


def render_finished():
    st.success("🎉 You finished all 50 starter levels!")
    st.write("You can keep improving the game by adding character upgrades, sound effects, more maps, and new bosses.")
    if st.button("Start Over", use_container_width=True):
        reset_game()
        st.rerun()


def sidebar():
    st.sidebar.markdown("# 🦖 Dino Controls")
    st.sidebar.write(f"Level: {st.session_state.level}/{MAX_LEVEL}")
    st.sidebar.write(f"Wins: {st.session_state.wins} | Losses: {st.session_state.losses}")
    st.sidebar.write(f"XP: {st.session_state.xp}")
    st.sidebar.progress(clamp(st.session_state.level / MAX_LEVEL))
    if st.sidebar.button("Start / Restart Current Level", use_container_width=True):
        start_level(st.session_state.level)
        st.rerun()
    if st.sidebar.button("New Game", use_container_width=True):
        reset_game()
        st.rerun()
    with st.sidebar.expander("How to play", expanded=False):
        st.write("Move with the arrow buttons. If the T-Rex bumps into a rock, he smashes it. If he bumps into a caveman or boss, he attacks. Find enough food to finish the level.")


def css():
    st.markdown(
        """
<style>
:root {
    --cream: #fff8e7;
    --ink: #172016;
    --deep: #0b3b24;
    --forest: #1f7a45;
    --leaf: #42b66b;
    --sun: #ffe08a;
    --rock: #d7d0c1;
    --card: #ffffff;
}
.stApp {
    background: linear-gradient(180deg, #e8ffe8 0%, #c5f6c9 34%, #86d993 100%);
    color: var(--ink);
}
/* Make text readable even when Streamlit theme defaults are dark. */
.stMarkdown, .stText, p, li, label, h1, h2, h3, h4, h5, h6, span, div {
    color: var(--ink);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7ffe9 0%, #d7f8cf 100%);
    border-right: 2px solid rgba(34, 96, 46, 0.25);
}
section[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: var(--ink) !important;
}
.story-card, .log-item {
    background: rgba(255, 255, 255, 0.92);
    border: 2px solid rgba(34, 96, 46, 0.18);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px rgba(18, 87, 40, 0.12);
    color: var(--ink) !important;
}
.hud {
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin: 12px 0 18px 0;
}
.hud span {
    background: #ffffff;
    color: var(--ink) !important;
    border: 2px solid rgba(34, 96, 46, 0.18);
    padding: 10px 14px;
    border-radius: 999px;
    font-weight: 800;
    box-shadow: 0 4px 10px rgba(18, 87, 40, 0.10);
}
.forest-grid {
    display:grid;
    gap:8px;
    padding: 14px;
    background: linear-gradient(135deg, #14552f, #1c7a43 55%, #134626);
    border-radius: 22px;
    border: 4px solid #6b4f2a;
    box-shadow: 0 18px 40px rgba(44, 86, 35, 0.25), inset 0 0 0 4px rgba(255,255,255,0.16);
    width: 100%;
}
.forest-cell {
    min-height: 76px;
    border-radius: 16px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    border: 2px solid rgba(255,255,255,0.55);
    box-shadow: inset 0 -10px 20px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.10);
    color: var(--ink) !important;
    overflow: hidden;
}
.forest-cell.terrain { background: linear-gradient(135deg, #76d46e, #3ea65c); }
.forest-cell.rock { background: linear-gradient(135deg, #eee3cf, #b8aa91); border-color:#fff7de; }
.forest-cell.enemy { background: linear-gradient(135deg, #ffd9a3, #ff9e52); border-color:#fff0c2; }
.forest-cell.boss { background: linear-gradient(135deg, #ffbd59, #e4572e); border-color:#fff0c2; }
.forest-cell.genie { background: linear-gradient(135deg, #d7c8ff, #8f79df); border-color:#ffffff; }
.forest-cell.ninja { background: linear-gradient(135deg, #dadada, #5a5a5a); border-color:#ffffff; }
.forest-cell.dino { background: linear-gradient(135deg, #fff176, #52c84d); border: 3px solid #fff7a8; transform: scale(1.03); }
.forest-cell:hover {
    transform: translateY(-2px);
    outline: 3px solid rgba(255, 247, 168, 0.85);
}
.cell-emoji {
    font-size: 34px;
    line-height: 1.05;
    min-height: 38px;
    color: var(--ink) !important;
}
.cell-label {
    font-size: 10px;
    line-height: 1.1;
    font-weight: 800;
    margin-top: 4px;
    color: #112115 !important;
    text-shadow: 0 1px rgba(255,255,255,0.55);
}
div.stButton > button {
    border-radius: 16px;
    min-height: 48px;
    font-weight: 900;
    color: #152015 !important;
    background: #ffffff !important;
    border: 2px solid rgba(34, 96, 46, 0.22) !important;
    box-shadow: 0 5px 12px rgba(18, 87, 40, 0.14);
}
div.stButton > button:hover {
    border-color: #1f7a45 !important;
    background: #fff8d7 !important;
}
[data-testid="stInfo"] {
    background: #fff8d7;
    color: var(--ink);
    border: 1px solid #e5c75d;
}
[data-testid="stCaptionContainer"] p {
    color: #1f3322 !important;
    font-weight: 600;
}
</style>
        """,
        unsafe_allow_html=True,
    )

def main():
    init_state()
    css()
    sidebar()
    screen = st.session_state.screen
    if screen == "intro":
        render_intro()
    elif screen == "play":
        render_play()
    elif screen == "won":
        render_won()
    elif screen == "lost":
        render_lost()
    elif screen == "mini":
        render_mini()
    elif screen == "finished":
        render_finished()


if __name__ == "__main__":
    main()
