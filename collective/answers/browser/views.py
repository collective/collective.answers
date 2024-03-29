import json
import logging

from zope.event import notify
from zope.security import checkPermission
from zope.lifecycleevent import ObjectModifiedEvent
from zExceptions import NotFound
from z3c.relationfield.relation import create_relation

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from collective.answers import MessageFactory as _
from collective.answers.answer import IAnswer
from collective.answers.utils import get_basic_mailsettings 

LOGGER = logging.getLogger('collective.answers: views')


class AddQuestionView(BrowserView):
    """ Add a question to the questions folder and associate it with the
        given context.
    """
    def __call__(self):
        if self.request.form.get('collective.answers.questionadd.form.submitted'):
            question = self.addQuestion()
            url = self.context.absolute_url()
            relatedContent = question.relatedContent.to_object
            if relatedContent:
                url = relatedContent.absolute_url()
            self.request.response.redirect(url)
            return
        return self.index()

    def addQuestion(self):
        request = self.request
        context = self.context

        question_text = request.get('question', '')
        if not question_text:
            return

        portal = context.restrictedTraverse('@@plone_portal_state').portal()
        questions = portal._getOb('questions')
        new_id = questions.generateId('question')
        relation = create_relation(context.getPhysicalPath())

        questions.invokeFactory('collective.answers.question',
                                id=new_id,
                                relatedContent=relation,
                                text=question_text.decode('utf-8'))
        
        question = questions._getOb(new_id)
        return question

    def addQuestionJSON(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        question = self.addQuestion() 
        message = "Question %s was added" %question.text
        view = question.restrictedTraverse('@@render-question')
        html = view()
        result = 'success'
        return json.dumps({'result'    : result,
                           'message'   : message,
                           'questionid': question.getId(),
                           'html'      : html})

    def getUUID(self):
        """ Return a uuid for the current context.
        """
        uuid = IUUID(self.context)
        return uuid


class DeleteQuestionView(BrowserView):
    def deleteQuestion(self):
        request = self.request
        context = self.context

        questionid = request.form.get('questionid')
        if questionid is None: return False

        portal = context.restrictedTraverse('@@plone_portal_state').portal()
        questions = portal._getOb('questions')
        questions._delObject(questionid)
        return True

    def deleteQuestionJSON(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        result = self.deleteQuestion() and 'success' or 'failure'
        message = "Question was deleted."
        questionid = self.request.get('questionid')
        if not result:
            message = "Question was not deleted."
            result = 'failure'
        return json.dumps({'result': result,
                           'message': message,
                           'questionid': questionid})


class AddAnswerView(BrowserView):
    """ Add an answer for a given the question.
    """

    def __call__(self):
        if self.request.form.get('collective.answers.qaviewlet.form.submitted'):
            answer = self.addAnswer()
            url = self.context.absolute_url()
            relatedContent = self.context.relatedContent.to_object
            if relatedContent:
                url = relatedContent.absolute_url()
            self.request.response.redirect(url)
            return
        else:
            return self.index() 

    def can_show(self):
        permission = 'collective answers: Add Answer'
        pmt = getToolByName(self.context, 'portal_membership')
        return pmt.checkPermission(permission, self.context) and True or False

    def addAnswer(self):
        request = self.request
        context = self.context

        answer_text = request['answer']
        portal = context.restrictedTraverse('@@plone_portal_state').portal()
        questions = portal._getOb('questions')

        questionid = self.request.get('questionid', None)
        question = questions._getOb(questionid)
        if not question:
            raise NotFound('The question %s could not be found.' %questionid)

        new_id = question.generateId('answer')

        question.invokeFactory('collective.answers.answer',
                                id=new_id)
        answer = question._getOb(new_id)
        # refer to: plone.app.textfield.tests for more info/examples  
        answer.text = IAnswer['text'].fromUnicode(answer_text.decode('utf-8'))

        notify(ObjectModifiedEvent(answer))
        return answer

    def addAnswerJSON(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        answer = self.addAnswer()
        if answer:
            message = "An answer was added."
            result = 'success'
            answerid = answer.getId()
            view = answer.restrictedTraverse('@@render-answer')
            html = view()
        else:
            message = 'Answer could not be added.'
            result = 'failure'
            answerid = ''
            html = ''
        return json.dumps({'result'  : result,
                           'message' : message,
                           'answerid': answerid,
                           'html'    : html})
    
    def allowQuestions(self):
        """ Check if the content in question (self.context) allows
            questions.
        """
        allow = getattr(self.context, 'allowQuestions', False)
        return allow

    def author(self, question):
        return question.Creator()

    def author_image(self, question):
        username = question.Creator()
        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            pmt = getToolByName(self.context, 'portal_membership')
            return pmt.getPersonalPortrait(username).absolute_url()
        
    def get_author_home_url(self, question):
        username = question.Creator()
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def can_delete(self, question):
        pmt = getToolByName(self.context, 'portal_membership')
        return pmt.checkPermission('Delete objects', question) and True or False

    def can_delete_answer(self, answer):
        pmt = getToolByName(self.context, 'portal_membership')
        member = pmt.getAuthenticatedMember().getId()
        if member is None:
            return False

        return answer.Creator() == member and True or False


class DeleteAnswerView(BrowserView):
    def deleteAnswer(self):
        request = self.request
        context = self.context

        questionid = request.form.get('questionid')
        answerid = request.form.get('answerid')
        if questionid is None or answerid is None: return False

        portal = context.restrictedTraverse('@@plone_portal_state').portal()
        questions = portal._getOb('questions')
        question = questions._getOb(questionid)
        question._delObject(answerid)
        return True

    def deleteAnswerJSON(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        result = self.deleteAnswer() and 'success' or 'failure'
        message = "Answer was deleted."
        answerid = self.request.form.get('answerid')
        if not result:
            message = "Answer was not deleted."
            result = 'failure'
        return json.dumps({'result': result,
                           'message': message,
                           'answerid': answerid})


class AnsweredMessageView(BrowserView):

    @property
    def question(self):
        return self.context.aq_parent
    
    def related_content(self):
        return self.question.relatedContent.to_object

    def get_safe_text(self, text):
        return text.decode('utf-8') 


class AnnotatorNotify(BrowserView):
    """ Send email notification to owner and every user that replied to a 
        specific annotation when a new reply is posted or deleted
    """

    def notifyJSON(self):
        # get the basic mail settings and details
        errors, mail_host, mail_from, mail_to = get_basic_mailsettings(self.context)
        if errors:
            for error in errors:
                LOGGER.warn(error)
            return errors

        # Compose email
        subject = _(u"Your question was answered.")
        message = "Annotator mail test"
        # Send email
        mail_host.secureSend(message, mail_to, mail_from, subject=subject)
        result = 'success'
        return json.dumps({'result' : result})

