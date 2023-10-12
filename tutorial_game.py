import random
import pyasge
from gamedata import GameData


def isInside(sprite, mouse_x, mouse_y) -> bool:
    bounds = sprite.getWorldBounds()
    if bounds.v1.x < mouse_x < bounds.v2.x and bounds.v1.y < mouse_y < bounds.v3.y:
        return True

    return False


class MyASGEGame(pyasge.ASGEGame):
    """
    The main game class
    """

    def __init__(self, settings: pyasge.GameSettings):
        """
        Initialises the game and sets up the shared data.

        Args:
            settings (pyasge.GameSettings): The game settings
        """
        pyasge.ASGEGame.__init__(self, settings)
        self.renderer.setClearColour(pyasge.COLOURS.BLACK)

        # create a game data object, we can store all shared game content here
        self.data = GameData()
        self.data.inputs = self.inputs
        self.data.renderer = self.renderer
        self.data.game_res = [settings.window_width, settings.window_height]

        # register the key and mouse click handlers for this class
        self.key_id = self.data.inputs.addCallback(pyasge.EventType.E_KEY, self.keyHandler)
        self.mouse_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_CLICK, self.clickHandler)

        # set the game to the menu
        self.game_state = 0
        self.menu = True
        self.play_option = None
        self.exit_option = None
        self.menu_option = 0

        # This is a comment
        self.data.background = pyasge.Sprite()
        self.initBackground()

        #
        self.menu_text = None
        self.initMenu()

        self.game_over = None
        self.initGameOver()

        # Scoreboard Shenanigans
        self.scoreboard = None
        self.initScoreboard()

        # This is a comment
        self.fish = pyasge.Sprite()
        self.initFish()

        # Fish Speeds + Timer Space
        self.speed = 350

        self.timer = None
        self.initTimer()
        self.timerCountdown = 15


    def initBackground(self) -> bool:
        if self.data.background.loadTexture("Data/images/background.png"):
            self.data.background.z_order = -100
            return True
        else:
            return False

    def initTimer(self) -> None:
        self.timer = pyasge.Text(self.data.fonts["MainFont"])
        self.timer.x = 15
        self.timer.y = 75
        self.timer.string = str(self.data.score).zfill(3)

    def initFish(self) -> bool:
        if self.fish.loadTexture("data/images/kenney_fishpack/fishtile_072.png"):
            self.fish.z_order = 1
            self.fish.scale = 1
            self.fish.x = 300
            self.fish.y = 300
            return True

        return False

    def initScoreboard(self) -> None:
        self.scoreboard = pyasge.Text(self.data.fonts["MainFont"])
        self.scoreboard.x = 1300
        self.scoreboard.y = 75
        self.scoreboard.string = str(self.data.score).zfill(6)

    def initMenu(self) -> bool:
        self.data.fonts["MainFont"] = self.data.renderer.loadFont("data/fonts/KGHAPPY.ttf", 64)
        self.menu_text = pyasge.Text(self.data.fonts["MainFont"])
        self.menu_text.string = "The Fish Game"
        self.menu_text.position = [100, 100]
        self.menu_text.colour = pyasge.COLOURS.DARKBLUE

        # Play Option
        self.play_option = pyasge.Text(self.data.fonts["MainFont"])
        self.play_option.string = ">Start"
        self.play_option.position = [100, 400]
        self.play_option.colour = pyasge.COLOURS.DARKBLUE

        # Exit Option
        self.exit_option = pyasge.Text(self.data.fonts["MainFont"])
        self.exit_option.string = "Exit"
        self.exit_option.position = [500, 400]
        self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
        return True

    def initGameOver(self) -> bool:
        self.data.fonts["MainFont"] = self.data.renderer.loadFont("data/fonts/KGHAPPY.ttf", 64)
        self.game_over = pyasge.Text(self.data.fonts["MainFont"])
        self.game_over.string = "Game Over!"
        self.game_over.position = [100, 100]
        self.game_over.colour = pyasge.COLOURS.DARKBLUE

        self.your_score = pyasge.Text(self.data.fonts["MainFont"])
        self.your_score.position = [100, 250]
        self.your_score.scale = 0.75
        self.your_score.colour = pyasge.COLOURS.DARKBLUE

        self.play_again = pyasge.Text(self.data.fonts["MainFont"])
        self.play_again.string = ">Replay"
        self.play_again.position = [100, 400]
        self.play_again.colour = pyasge.COLOURS.DARKBLUE

        self.quit_game = pyasge.Text(self.data.fonts["MainFont"])
        self.quit_game.string = "Exit"
        self.quit_game.position = [500, 400]
        self.quit_game.colour = pyasge.COLOURS.LIGHTSLATEGREY
        return True

    def clickHandler(self, event: pyasge.ClickEvent) -> None:
        if event.action == pyasge.MOUSE.BUTTON_PRESSED and event.button == pyasge.MOUSE.MOUSE_BTN1:
            if isInside(self.fish, event.x, event.y):
                self.data.score += 1
                self.scoreboard.string = str(self.data.score).zfill(6)
                self.spawn()

    def keyHandler(self, event: pyasge.KeyEvent) -> None:

        if event.action == pyasge.KEYS.KEY_PRESSED:

            # main menu
            if event.key == pyasge.KEYS.KEY_RIGHT or event.key == pyasge.KEYS.KEY_LEFT:
                self.menu_option = 1 - self.menu_option
                if self.menu_option == 0:
                    self.play_option.string = ">Start"
                    self.play_option.colour = pyasge.COLOURS.DARKBLUE
                    self.exit_option.string = "Exit"
                    self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY

                elif self.menu_option == 1:
                    self.play_option.string = "Start"
                    self.play_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                    self.exit_option.string = ">Exit"
                    self.exit_option.colour = pyasge.COLOURS.DARKBLUE

            if event.key == pyasge.KEYS.KEY_ENTER:
                if self.menu_option == 0:
                    self.menu = False
                    self.game_state = 1
                    self.spawn()
                    self.timerCountdown = 15
                else:
                    self.signal_exit()


    def spawn(self) -> None:
        # Fish 1
        x = random.randint(0, self.data.game_res[0] - self.fish.width)
        y = random.randint(0, self.data.game_res[1] - self.fish.height)
        self.fish.x = x
        self.fish.y = y

    def update(self, game_time: pyasge.GameTime) -> None:

        if self.menu:
            # update the menu here
            pass
        else:
            # update the game here
            self.fish.x += self.speed * game_time.fixed_timestep
            if self.fish.x > self.data.game_res[0]:
                self.fish.x = -self.fish.width

            self.timerCountdown -= game_time.fixed_timestep
            self.timer.string = str(int(self.timerCountdown)).zfill(3)
            if int(self.timerCountdown) <= 0:
                self.game_state = 2

    def render(self, game_time: pyasge.GameTime) -> None:
        """
        This is the variable time-step function. Use to update
        animations and to render the gam    e-world. The use of
        ``frame_time`` is essential to ensure consistent performance.
        @param game_time: The tick and frame deltas.
        """

        self.data.renderer.render(self.data.background)

        if self.game_state == 0:
            # Menu Content
            self.data.renderer.render(self.menu_text)
            self.data.renderer.render(self.play_option)
            self.data.renderer.render(self.exit_option)

        elif self.game_state == 1:
            # Main Game Content
            self.data.renderer.render(self.fish)
            self.data.renderer.render(self.scoreboard)
            self.data.renderer.render(self.timer)


        elif self.game_state == 2:
            # render the Game Over
            self.data.renderer.render(self.game_over)
            self.data.renderer.render(self.your_score)
            self.data.renderer.render(self.play_again)
            self.data.renderer.render(self.quit_game)



def main():
    """
    Creates the game and runs it
    For ASGE Games to run they need settings. These settings
    allow changes to the way the game is presented, its
    simulation speed and also its dimensions. For this project
    the FPS and fixed updates are capped at 60hz and Vsync is
    set to adaptive.
    """
    settings = pyasge.GameSettings()
    settings.window_width = 1600
    settings.window_height = 900
    settings.fixed_ts = 60
    settings.fps_limit = 60
    settings.window_mode = pyasge.WindowMode.BORDERLESS_WINDOW
    settings.vsync = pyasge.Vsync.ADAPTIVE
    game = MyASGEGame(settings)
    game.run()


if __name__ == "__main__":
    main()
