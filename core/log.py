## Journalisation des erreurs

from logging import getLogger


class Log:

    # Récupération du nom de la classe dérivée pour l'afficher dans le journal d'erreur

    @property
    def logger(self):

        return getLogger(self.__class__.__name__)


