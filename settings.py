from pygame import mixer
mixer.pre_init(44100, -16, 1, 512)
mixer.init()
mixer.music.set_volume(0)

FPS = 30
CELL_SIZE = 150
MARGIN_X = 160
MARGIN_Y = 60
WIDTH = CELL_SIZE * 3 + MARGIN_X * 4
HEIGHT = CELL_SIZE * 3 + MARGIN_Y * 2

GATE_UNLOCK = mixer.Sound('src/audio/gate_unlock.wav')
SWORD_1 = mixer.Sound('src/audio/sword_1.wav')
SWORD_2 = mixer.Sound('src/audio/sword_2.wav')
SHIELD = mixer.Sound('src/audio/shield.wav')
CLICK = mixer.Sound('src/audio/click.wav')

GATE_UNLOCK.set_volume(0.5)
SWORD_1.set_volume(0.5)
SWORD_2.set_volume(0.5)
SHIELD.set_volume(0.5)
CLICK.set_volume(0.2)
