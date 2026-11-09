from src.data.colors import RED, GREEN, YELLOW

def human_play(env, info):
    legal_move_tuples = []    

    for legal_move in info["legal_moves"]:
        move_tuple = tuple(prop for prop in legal_move)
        legal_move_tuples.append(move_tuple)

    is_placing = all(src == 0 for src, _, _, in legal_move_tuples)
    sources = sorted({ src for src, _, _ in legal_move_tuples })

    stage = "dst"
    if not is_placing: stage = "src"

    src = 0
    if not is_placing: src = None

    dst = None

    def repaint():
        env.clear_markings()

        if stage == "src":
            for source in sources: env.mark_position(source, YELLOW)

        elif stage == "dst":
            if not is_placing: env.mark_position(src, YELLOW)

            for current_src, current_dst, _ in legal_move_tuples:
                if current_src == src: env.mark_position(current_dst, GREEN)
            
        else:
            for current_src, current_dst, current_capture in legal_move_tuples:
                if current_src == src and current_dst == dst: env.mark_position(current_capture, RED)

    repaint()

    while True:
        interaction = env.interact()

        if interaction["type"] == "quit": return None

        if interaction["type"] == "key_press":
            if interaction["key"] == "escape": return None
            continue

        if interaction["type"] != "mouse_click" or interaction["position"] == 0: continue

        position = interaction["position"]

        if stage == "src":
            if position in sources:
                src = position
                stage = "dst"

        elif stage == "dst":
            if not is_placing and position == src:
                src = None
                stage = "src"

            elif not is_placing and position in sources:
                src = position

            else:
                captures = []

                for current_src, current_dst, current_capture in legal_move_tuples:
                    if current_src == src and current_dst == position: captures.append(current_capture)

                if captures:
                    dst = position

                    if captures == [0]:
                        env.clear_markings()
                        return [src, dst, 0]

                    stage = "capture"

        else:
            if (src, dst, position) in legal_move_tuples:
                env.clear_markings()
                return [src, dst, position]

        repaint()