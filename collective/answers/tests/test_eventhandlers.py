import os

from Acquisition import aq_base

from zope.component import getSiteManager
from zope.component import eventtesting
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import ObjectModifiedEvent

from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

from base import CollectiveAnswersTestBase

from collective.answers.interfaces import ICollectiveAnswersLayer
from collective.answers.question import IQuestion
from collective.answers.eventhandlers import questionAnswered

dirname = os.path.dirname(__file__)


class TestEventHandlers(CollectiveAnswersTestBase):
    """ Test the event handlers.
    """
    def setUp(self):
        super(TestEventHandlers, self).setUp()
        eventtesting.setUp()
        self.setupMailHost()

    def beforeTearDown(self):
        self.restoreMailHost()

    def _test_question_answered(self):
        context = self.portal.questions
        manager_name = 'plone.belowcontent'
        viewlet_name = 'question-add'
        layer = ICollectiveAnswersLayer
        viewlet = self._find_viewlet(context, manager_name, viewlet_name, layer)

        question = self._createQuestion()
        eventtesting.clearEvents()
        request = self.portal.REQUEST
        request.form['collective.answers.questionslist.form.submitted'] = 'submitted'
        request.form['questionid'] = question.getId()
        request.form['answer'] = 'first answer'
        request.form['action'] = 'add-answer'
        viewlet[0].update()

        events = eventtesting.getEvents(
            IObjectModifiedEvent,
            filter=lambda obj: IQuestion.providedBy(obj)
        )
        self.assertTrue(len(events) > 0, 'Missing event.')

    def test_questionAnswered_incorrect_data(self):
        question = self._createQuestion()

        event = ObjectModifiedEvent(question)
        reported_errors = questionAnswered(question, event)

        self.assertTrue(len(reported_errors) > 0, 'No errors were reported.')
        expected_errors = \
            ['The owner () has no email address!', 'Add a portal email address.']
        for error in expected_errors:
            self.assertTrue(
                error in reported_errors,
                'The error %s was not reported.' %error
        )
    
    def test_questionAnswered(self):
        question = self._createQuestion()
        pmt = self.portal.portal_membership
        pmt.getMemberById('test_user_1_').setMemberProperties(
            {'email': 'tester@example.com'})
        self.portal.email_from_address = 'admin@example.com'
        self.portal.REQUEST['ACTUAL_URL'] = 'example.com'
        event = ObjectModifiedEvent(question)
        errors = questionAnswered(question, event)
        
        mailhost = self.portal.MailHost
        self.assertTrue(errors is None, 'Errors were reported.')
        self.assertTrue(mailhost.messages, 'No message in mailhost.')

        file = open(os.path.join(
            dirname, 'data', 'message.txt'), 'r')
        reference_message = file.read()
        file.close()
        returned_message = mailhost.messages[0]
        self.assertEqual(returned_message, reference_message,
            'Returned message and reference message '
            'are not identical: \n\n%s' % self.diff(
                returned_message, reference_message))

    def setupMailHost(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def restoreMailHost(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)

