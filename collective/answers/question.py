from five import grok
from zope import schema
from z3c.relationfield.schema import RelationChoice

from plone.indexer import indexer
from plone.uuid.interfaces import IUUID
from plone.directives import dexterity, form
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective.answers import MessageFactory as _


class IQuestion(form.Schema):
    """
    Question
    """
    """
    A question about a piece of content.
    """

    text = schema.Text(
        title=_(u"Question"),
        description=_("The question."),
        required=True,
    )

    relatedContent = RelationChoice(
        title=_(u'label_content_item', default=u'Related Content'),
        source=ObjPathSourceBinder(
          object_provides='Products.CMFCore.interfaces._content.IContentish'),
        required=False,
    )


@indexer(IQuestion)
def relatedContentUID(obj):
    uuid = IUUID(obj.relatedContent.to_object)
    return uuid
grok.global_adapter(relatedContentUID, name="relatedContentUID")


class Question(dexterity.Container):
    grok.implements(IQuestion)
    
    def Title(self):
        return self.text

    def setTitle(self, value):
        pass

    @property
    def answers(self):
        return self.getAnswers()

    def getAnswers(self):
        obs = self.objectValues()
        return [ob for ob in obs if ob.portal_type == 'collective.answers.answer']
