# ------------------ Imports ------------------
from wtforms.widgets import HTMLString, html_params

# ------------------ Widget ------------------
__all__ = ["ButtonWidget"]


class ButtonWidget(object):
    """
    Widget for ButtonField.
    """

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if "value" not in kwargs:
            kwargs["value"] = field._value()

        return HTMLString(
            "<button {params}>{label}</button>".format(
                params=self.html_params(name=field.name, **kwargs),
                label=field.label.text,
            )
        )
