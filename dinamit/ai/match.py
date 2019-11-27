import nltk


class DomainRuleMatcher(object):
    def __init__(self, pattern):
        self.tagger = nltk.RegexpTagger(pattern)

    def match(self, domain):
        return self.tagger.tag([domain])[0]
