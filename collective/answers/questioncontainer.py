from five import grok
from plone.directives import dexterity, form

from collective.answers import MessageFactory as _


class IQuestionContainer(form.Schema):
    """
    Question container
    """

class QuestionContainer(dexterity.Container):
    grok.implements(IQuestionContainer)
