from five import grok

from plone.directives import dexterity, form
from plone.app.textfield import RichText

from collective.answers import MessageFactory as _


# Interface class; used to define content-type schema.

class IAnswer(form.Schema):
    """
    Answer
    """
    text = RichText(
        title=_(u"Answer"),
        description=_("The answer."),
        required=True,
    )


class Answer(dexterity.Item):
    grok.implements(IAnswer)
