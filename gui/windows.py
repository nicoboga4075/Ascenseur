## Interface graphique

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject
from core.log import Log
from core.structures import Batiment

ICON_WINDOW = "./Pavillon.jpg"


class Params:

    nb_etages = None
    nb_asc = None

    def __init__(self, nb_etages, nb_asc):
        self.nb_etages = nb_etages
        self.nb_asc = nb_asc

    def __repr__(self):
        return "Etages: %d - Asc.: %d" % \
            (self.nb_etages, self.nb_asc)


class AppWindow(Gtk.Application, Log):

    # Composants graphiques

    widgets = None
    batiment = None

    # Rafraichissement du dessin périodiquement

    _timer = None

    # Options modifiables

    params = None

    def __init__(self):

        Gtk.Application.__init__(self)
        self.widgets = {}

        # Valeurs par défaut

        self.params = Params(nb_etages = 7, nb_asc = 2)

    def do_activate(self):
        """
        Cette fonction est appelée quand l'OS lance l'application.
        """
        window = Gtk.ApplicationWindow(application = self)
        self.widgets["window"] = window
        window.set_title("Simulateur")
        window.set_icon_from_file(ICON_WINDOW)
        window.set_titlebar(self.make_headerbar())
        window.connect("delete_event", self.on_delete_event)
        self.widgets["btn_stop"].set_sensitive(False)
        # dimensionnement de la fenêtre et de la zone de dessin
        self._redimensionner()
        window.set_resizable(False)
        window.show_all()

    def do_startup(self):
        """
        Initialise l'application au lancement de sa 1ere instance.
        """
        Gtk.Application.do_startup(self)

    def on_delete_event(self, gtk_widget, event):
        """ Arrêt de l'application """
        self.on_sim_stop(None)
        Gtk.Application.quit(self)

    def on_sim_start(self, gtk_widget):
        """
        Démarrer une simulation.
        @type  gtk_widget: Button
        @param gtk_widget: Composant lié à l'événement
        """
        self.logger.debug("Démarrage d'une simulation...")
        # activation du bouton stop et désactivation du bouton start
        self.widgets["btn_start"].set_sensitive(False)
        self.widgets["btn_stop"].set_sensitive(True)
        # initialisation
        self.batiment = Batiment(self.widgets["area"], self.params)
        # on démarre le rafraîchissement régulier du dessin,
        # mais on peut l'optimiser en ne l'activant que durant une animation
        self._timer = GObject.timeout_add(200, self.__area_refresh_timeout)
        self.logger.debug("Démarrage de la simulation (%s)." % self.params)

    def _redimensionner(self):
        """
        Détermine la dimension de la fenêtre et de la zone de dessin.
        """
        # suppression de la zone de dessin si elle existe pour la créer
        # avec les dimensions voulues
        window = self.widgets["window"]
        try:
            area = self.widgets["area"]
            window.remove(area)
        except:
            # self.logger.debug("Pas de zone de dessin à remplacer.")
            pass
        # construction du nouveau composant graphique
        area = Gtk.DrawingArea()
        self.widgets["area"] = area
        window.add(area)
        # définition des dimensions requises
        larg = 1800
        ht = 1000
        window.set_default_size(larg, ht)

        area.connect("draw", self.on_draw)
        area.set_size_request(larg, ht)
        area.show()

    def on_sim_stop(self, gtk_widget):
        """
        Arrête une simulation.
        @type  gtk_widget: Gtk.Button
        @param gtk_widget: Composant lié à l'événement
        """
        # arrêt des ascenseurs et du simulateur d'appels
        if self.batiment:
            for asc in self.batiment.automate.ascenseurs:
                asc.on_simu_stop()
                self.batiment.sim_appels.flg_stop = True
            self.batiment = None
        if gtk_widget:
            # s'il ne s'agit pas d'un arrêt forcé suite à la modification
            # des options sans avoir lancé de simulation
            GObject.source_remove(self._timer)
            self._timer = None
            # on s'assure d'un dernier rafraichissement pour effacer le dessin
            self.__area_refresh_timeout()
        # déactivation du bouton stop et sactivation du bouton start
        self.widgets["btn_stop"].set_sensitive(False)
        self.widgets["btn_start"].set_sensitive(True)
        self.logger.debug("Arrêt de la simulation.")


    def on_draw(self, area, context):
        """
        Actualisation du dessin demandée par Gtk.
        @type  area: DrawingArea
        @param area: Composant lié à l'événement
        @type  context: cairo context
        @param context: Surface de dessin
        """
        # arrière-plan
        color = Gdk.RGBA()
        color.parse("#000")
        area.override_background_color(0, color)
        # dessin du bâtiment (qui dessinera le reste)
        if self.batiment:
            self.batiment.dessiner(area, context)


    def __area_refresh_timeout(self):
        """
        Demande un refraîchissement du dessin.
        """
        self.widgets["area"].queue_draw()
        # réactive le timer
        return True

    def make_headerbar(self):

        # Création de l'en-tête pour l'application

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Pavillon de l'humanité"

        # Bouton démarrer

        btn_start = Gtk.Button()
        icon = Gio.ThemedIcon(name = "media-playback-start")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn_start.add(image)
        btn_start.connect("clicked", self.on_sim_start)
        self.widgets["btn_start"] = btn_start

        # Bouton arrêter

        btn_stop = Gtk.Button()
        icon = Gio.ThemedIcon(name = "media-playback-stop")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn_stop.add(image)
        btn_stop.connect("clicked", self.on_sim_stop)
        self.widgets["btn_stop"] = btn_stop

        # Bouton options

        btn_options = Gtk.Button()
        icon = Gio.ThemedIcon(name = "document-properties")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn_options.add(image)
        btn_options.connect("clicked", self.configuration)
        self.widgets["btn_options"] = btn_options

        # Groupe des boutons de gauche

        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        box.add(btn_start)
        box.add(btn_stop)
        box.add(btn_options)
        hb.pack_start(box)


        return hb

    def configuration(self, gtk_widget):

        cfg = ConfigDialog(self.widgets["window"])

        # Affichage des paramètres de simulation

        reponse = cfg.run()

        if reponse == Gtk.ResponseType.OK:

            self.on_sim_stop(None) # Arrêt de la simulation s'il y en a une en cours

            self.params = Params(nb_etages = 7, nb_asc = int(cfg.spin_asc.get_value()))

            self._redimensionner()

        cfg.destroy()


class ConfigDialog(Gtk.Dialog):

    # Configuration des options

    spin_asc = None


    def __init__(self, parent = None):

        Gtk.Dialog.__init__(self, "Configuration", parent, 0,(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # Layer contenant les lignes d'options

        vertical_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        # Nombre d'ascenseurs

        hbox_asc = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        adj = Gtk.Adjustment(value = 2, lower = 2, upper = 3,step_increment = 1)
        spin_asc = Gtk.SpinButton()
        spin_asc.set_adjustment(adj)
        spin_asc.set_numeric(True)
        spin_asc.set_digits(0)
        self.spin_asc = spin_asc
        lbl = Gtk.Label("Nombre d'ascenseurs : ")
        hbox_asc.add(lbl)
        hbox_asc.add(spin_asc)
        vertical_box.add(hbox_asc)

        # Insertion du contenu

        gen_box = self.get_content_area()
        gen_box.add(vertical_box)
        self.show_all()
