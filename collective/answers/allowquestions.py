from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.directives import form
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form.interfaces import IEditForm, IAddForm
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective.answers import MessageFactory as _


class IAllowQuestions(form.Schema):
    """
       Marker/Form interface for Allow questions
    """
    form.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=['allowQuestions',],
        )

    allowQuestions = schema.Bool(
           title = _(u"label_allowquestions", default=u"Allow questions"),
           required=False,
           default=False,
           )
   
    form.omitted('allowQuestions')
    form.no_omit(IEditForm, 'allowQuestions')
    form.no_omit(IAddForm, 'allowQuestions')
   
alsoProvides(IAllowQuestions,IFormFieldProvider)

