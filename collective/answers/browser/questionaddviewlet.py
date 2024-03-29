from plone.app.layout.viewlets.common import ViewletBase
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.answers import MessageFactory as _

class QuestionAddViewlet(ViewletBase):
    """ Display a form to add a new question.
    """
    index = ViewPageTemplateFile('questionaddviewlet_templates/addform.pt')

    def update(self):
        super(QuestionAddViewlet, self).update()

        if self.request.form.get('collective.answers.questionadd.form.submitted'):
            view = self.context.restrictedTraverse('@@add-question')
            question = view()
            self.request.response.redirect(self.context.absolute_url())

    def render(self):
        """ We render an empty string when a specific piece of content
            does not allow questions.
        """
        if self.allowQuestions():
            return super(QuestionAddViewlet, self).render()
        else:
            return ""
    
    def allowQuestions(self):
        """ Check if the content in question (self.context) allows
            questions.
        """
        allow = getattr(self.context, 'allowQuestions', False)
        return allow

    def getUUID(self):
        """ Return a uuid for the current context.
        """
        uuid = IUUID(self.context)
        return uuid
