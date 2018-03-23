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

    def addRule(self, ruleName, toPathFormat, fromPathRegex):
        self.__ruleMap[ruleName] = {
            RuleEnum.kToPathFormat: "{{:{}}}".format(toPathFormat),
            RuleEnum.kFromTemplateName: fromPathRegex
        }

    def path(self, templateName, fields):
        template = self.__templateExpander(templateName)

        return self.__templateParser(template, fields)

    def templateName(self, path):
        pass

    def fields(self, templateName, path):
        pass

    def paths(self, templateName, fields):
        pass

    def __templateParser(self, template, fields):
        path = template

        for regex in _TEMPLATE_REGEX.finditer(template):
            key = regex.group(1)

            if key in fields:
                field = fields[key]

                if key in self.__ruleMap:
                    pattern = self.__ruleMap[key][RuleEnum.kToPathFormat]
                    field = pattern.format(fields[key])
                else:
                    field = str(field)

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
