import re

class Condition:
    def match(self, line):
        """
            Function that verifies if the  
            condition is accomplished in this line
        """
        matched = self.match_line(line)
        if matched:
            self.times_matched +=1
            return self.times_matched >= self.times
        return False

    def condition_name(self):
        return self.name

    def restart(self):
        """
            Rollsback if there is some kind of state in the condition
        """
        self.times_matched = 0

class RegexCondition(Condition):
    def __init__(self, name=None, regex=None, icase=False, times=1, **kwargs):
        assert times >= 1
        self.name = name 
        self.times = times
        self.times_matched = 0
        
        if icase:
            self.regex = re.compile(regex, re.IGNORECASE)
        else:
            self.regex = re.compile(regex)

    def match_line(self, line):
        return re.search(self.regex, line)

class StringCondition(Condition):
    def __init__(self, name=None, string=None, icase=False, times=1, **kwargs):
        assert times >= 1
        self.name = name 
        self.times = times
        self.times_matched = 0
        self.icase = icase
        self.string = string.lower() if icase else string

    def match_line (self, line):
        if self.icase:
            line = line.lower()
        return self.string in line