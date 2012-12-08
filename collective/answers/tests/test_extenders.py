import os

from base import CollectiveAnswersTestBase

from collective.answers.interfaces import IcollectiveanswersLayer

dirname = os.path.dirname(__file__)


class TestAllowQuestionsSchemaExtender(CollectiveAnswersTestBase):
    """ Test the schema extender that enables questions on
        archetypes content.
    """
    
    def test_questions_disabled(self):
        self.portal.invokeFactory('Document', id='test_page')
        context = self.portal.test_page
        context.allowQuestions = False

        manager_name = 'plone.belowcontent'
        viewlet_name = 'question-add'
        layer = IcollectiveanswersLayer
        viewlet = self._find_viewlet(context, manager_name, viewlet_name, layer)
        
        self.assertTrue(
            viewlet[0].render() ==  "",
            'Questions are disable; viewlet should not render.'
        )

    def test_questions_enabled(self):
        self.portal.invokeFactory('Document', id='test_page')
        context = self.portal.test_page
        context.allowQuestions = True

        manager_name = 'plone.belowcontent'
        viewlet_name = 'question-add'
        layer = IcollectiveanswersLayer
        viewlet = self._find_viewlet(context, manager_name, viewlet_name, layer)
        
        self.assertTrue(
            len(viewlet[0].render()) > 0,
            'Questions are enabled; viewlet should render.'
        )
