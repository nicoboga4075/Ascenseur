import sys
from gui.windows import AppWindow
from logging import StreamHandler, Formatter, getLogger, DEBUG

# Journalisation des erreurs

logger = getLogger()


if __name__ == '__main__':

    # Journalisation dans la console

    logger.setLevel(DEBUG)

    pattern = "[%(levelname)s:%(name)s] %(message)s"

    sh = StreamHandler()

    sh.setFormatter(Formatter(pattern))

    logger.addHandler(sh)

    # Initialisation de l'affichage

    application = AppWindow()

    application.run(sys.argv)

