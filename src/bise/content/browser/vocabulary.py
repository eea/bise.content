from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@provider(IVocabularyFactory)
def eunis_group_vocabulary(context):
    """Return a vocabulary of EUNIS groups."""
    terms = [
        SimpleTerm(value='Group 1', token='group_1', title='Group 1'),
        SimpleTerm(value='Group 2', token='group_2', title='Group 2'),
        SimpleTerm(value='Group 3', token='group_3', title='Group 3'),
        SimpleTerm(value='Group 4', token='group_4', title='Group 4'),
        SimpleTerm(value='Group 5', token='group_5', title='Group 5'),
        SimpleTerm(value='Group 6', token='group_6', title='Group 6'),
        SimpleTerm(value='Group 7', token='group_7', title='Group 7'),
    ]
    return SimpleVocabulary(terms)
