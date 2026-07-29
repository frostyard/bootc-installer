"""Post-success acknowledgement for the next-boot MokManager action."""

from gi.repository import Adw, GObject, Gtk


@Gtk.Template(resource_path="/org/bootcinstaller/Installer/gtk/mok-enrollment.ui")
class BootcMokEnrollment(Adw.Bin):
    __gtype_name__ = "BootcMokEnrollment"
    __gsignals__ = {
        "mok-enrollment-acknowledged": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    ack_check = Gtk.Template.Child()
    btn_continue = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    password_value = Gtk.Template.Child()
    operator_password_note = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window
        self.delta = False
        self.ack_check.connect("toggled", self.__on_ack_toggled)
        self.btn_continue.connect("clicked", self.__on_continue)
        self.prepare()

    def prepare(self, password: str = "", parent_generated: bool = False):
        self.password_row.set_visible(parent_generated)
        self.password_value.set_text(password if parent_generated else "")
        self.operator_password_note.set_visible(not parent_generated)
        if parent_generated:
            self.ack_check.set_label("I have recorded this one-time MOK password")
        else:
            self.ack_check.set_label("I have the operator-provided MOK password")
        self.ack_check.set_active(False)
        self.btn_continue.set_sensitive(False)

    def __on_ack_toggled(self, check):
        self.btn_continue.set_sensitive(check.get_active())

    def __on_continue(self, *args):
        self.password_value.set_text("")
        self.emit("mok-enrollment-acknowledged")
