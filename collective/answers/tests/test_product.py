import os

from Products.CMFCore.utils import getToolByName
from plone.browserlayer.utils import registered_layers

from collective.answers.interfaces import ICollectiveAnswersLayer

from base import collectiveanswersTestBase

dirname = os.path.dirname(__file__)


class TestProductInstallation(collectiveanswersTestBase):
    def test_layer(self):
        self.assertTrue(
            ICollectiveAnswersLayer in registered_layers(),
            'Custom layer not available.'
        )

    def test_setuphandlers(self):
        self.assertTrue(
            'questions' in self.portal.objectIds(),
            'Questions folder was not created.'
        )
        questions = self.portal._getOb('questions')
        wft = getToolByName(self.portal, 'portal_workflow')
        self.assertEqual(
            wft.getInfoFor(questions, 'review_state'), 'private')
