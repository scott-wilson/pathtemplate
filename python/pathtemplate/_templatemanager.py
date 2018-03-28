import re
import os

_TEMPLATE_REGEX = re.compile(r'\{[\t ]*(.+?)[\t ]*\}')


class TemplateManager(object):
    def __init__(self):
        self.__ruleMap = {}
        self.__templateMap = {}

    def addTemplate(self, templateName, template, rootTemplateName=None):
        self.__templateMap[templateName] = {
            TemplateEnum.kTemplate: template,
            TemplateEnum.kRootTemplateName: rootTemplateName,
        }

    def addRule(self, ruleName, toPathFormat=None, fromPathRegexPattern=None, type=None):
        formatPattern = "{}"
        regexPattern = r'.+'

        if toPathFormat:
            formatPattern = "{{:{}}}".format(toPathFormat)
        if fromPathRegexPattern:
            regexPattern = fromPathRegexPattern

        self.__ruleMap[ruleName] = {
            RuleEnum.kToPathFormat: formatPattern,
            RuleEnum.kFromTemplateName: regexPattern,
            RuleEnum.kType: type
        }

    def path(self, templateName, fields):
        template = self.__templateExpander(templateName)

        return self.__templateParser(template, fields)

    def templateName(self, path):
        path = path.replace('\\', '/')
        templateNames = []

        for templateName in self.__templateMap:
            fields = self.fields(templateName, path)

            if self.path(templateName, fields) == path:
                templateNames.append(templateName)

        if not templateNames:
            raise ValueError("There are no template names for the given path.")
        elif len(templateNames) > 1:
            templateNames.sort()
            raise ValueError("There's more than one possible template names for the given path. The possible ones are {}".format(templateNames))

        return templateNames[0]

    def fields(self, templateName, path):
        template = self.__templateExpander(templateName)
        elements = []

        start = 0
        end = 0

        for regex in _TEMPLATE_REGEX.finditer(template):
            key = regex.group(1)
            end = regex.start()
            element = template[start:end]

            if not _TEMPLATE_REGEX.search(element):
                elements.append(re.escape(element))

            pattern = r'(?P<{}>{})'.format(key, self.__fromPath(key))
            elements.append(pattern)

            start = regex.start()
            end = regex.end()

        if end < len(template):
            elements.append(re.escape(template[end:]))

        regex = re.compile(r'^{}$'.format(''.join(elements)))
        result = regex.search(path)

        if result:
            result = result.groupdict().iteritems()
            return {k: self.__convertToType(k, v) for k, v in result}

        return {}

    def paths(self, templateName, fields):
        pass

    def __toPath(self, key):
        pattern = "{}"

        if key in self.__ruleMap:
            pattern = self.__ruleMap[key][RuleEnum.kToPathFormat]

        return pattern

    def __fromPath(self, key):
        pattern = r'.+'

        if key in self.__ruleMap:
            pattern = self.__ruleMap[key][RuleEnum.kFromTemplateName]

        return pattern

    def __convertToType(self, key, value):
        if key in self.__ruleMap:
            type = self.__ruleMap[key][RuleEnum.kType]

            if type is not None:
                return type(value)

        return value

    def __templateParser(self, template, fields):
        path = template

        for regex in _TEMPLATE_REGEX.finditer(template):
            key = regex.group(1)

            if key in fields:
                pattern = self.__toPath(key)
                field = pattern.format(fields[key])
                path = path.replace(regex.group(0), field)

        return path

    def __templateExpander(self, templateName):
        templates = []

        while templateName in self.__templateMap:
            template = self.__templateMap[templateName]
            templates.append(template[TemplateEnum.kTemplate])
            templateName = template[TemplateEnum.kRootTemplateName]

        templates.reverse()

        return os.path.join(*templates).replace('\\', '/')


class TemplateEnum(object):
    kTemplate = 0
    kRootTemplateName = 1


class RuleEnum(object):
    kToPathFormat = 0
    kFromTemplateName = 1
    kType = 2
