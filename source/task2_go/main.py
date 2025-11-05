import pygame
from ui.menu import MenuScene
from ui.game_scene import GameScene
from core.move import Move
from core.agents.human_agent import HumanAgent

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 900))
    pygame.display.set_caption("Go 9x9 — PvP / VsAI")
    clock = pygame.time.Clock()

    scene = "menu"; menu = MenuScene(screen); game = None; running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: running = False
            if scene == "game" and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                game.handle_click(e.pos)
            if scene == "game" and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    scene = "menu"; menu = MenuScene(screen)
                if e.key == pygame.K_SPACE:
                    player = game.state.to_play
                    agent = game.agents[player]
                    if isinstance(agent, HumanAgent):
                        agent.set_pending_move(Move.pass_())

        if scene == "menu":
            cfg = menu.run_once(events)
            if cfg is not None:
                game = GameScene(screen, cfg); scene = "game"
        elif scene == "game":
            game.step(); game.draw()

        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
