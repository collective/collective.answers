import os

from Products.CMFCore.utils import getToolByName

from base import CollectiveAnswersTestBase

from collective.answers.interfaces import ICollectiveAnswersLayer

dirname = os.path.dirname(__file__)


class TestAllowQuestionsBehavior(CollectiveAnswersTestBase):
    """ Test the behavior that enables questions on dexterity content.
    """
    
    def test_questions_disabled(self):
        types = getToolByName(self.portal, 'portal_types')
        fti = types.getTypeInfo('collective.answers.question')
        fti.behaviors = \
            ('collective.answers.behaviors.allowquestionsbehavior.IAllowQuestionsBehavior',)
        
        context = self._createQuestion()
        manager_name = 'plone.belowcontent'
        viewlet_name = 'question-add'
        layer = ICollectiveAnswersLayer
        viewlet = self._find_viewlet(context, manager_name, viewlet_name, layer)
        
        self.assertTrue(
            viewlet[0].render() ==  "",
            'Questions are disable; viewlet should not render.'
        )

    def test_questions_enabled(self):
        types = getToolByName(self.portal, 'portal_types')
        fti = types.getTypeInfo('collective.answers.question')
        fti.behaviors = \
            ('collective.answers.behaviors.allowquestionsbehavior.IAllowQuestionsBehavior',)
        
        context = self._createQuestion()
        context.allowQuestions = True
        manager_name = 'plone.belowcontent'
        viewlet_name = 'question-add'
        layer = ICollectiveAnswersLayer
        viewlet = self._find_viewlet(context, manager_name, viewlet_name, layer)
        
        self.assertTrue(
            len(viewlet[0].render()) > 0,
            'Questions are enabled; viewlet should render.'
        )
