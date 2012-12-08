import logging

log = logging.getLogger('collective.answers-setuphandlers')


def setupAnswers(portal):
    """ Create the basic structure and do initial configuration.
    """
    sections = [
        {'id': 'questions',
        'type': 'collective.answers.questioncontainer',
        'title': 'Questions',
        'exclude_from_nav': True,
        },
    ]

    for section_dict in sections:
        if not portal.hasObject(section_dict['id']):
            portal.invokeFactory(
                type_name=section_dict['type'],
                id=section_dict['id'],
                title=section_dict['title'],
                exclude_from_nav=section_dict.get('exclude_from_nav', False),
            )


def setupVarious(context):
    if context.readDataFile('collective.answers.txt') is None:
        return
    site = context.getSite()
    setupAnswers(site)
