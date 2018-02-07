import base64

from languages import languages_ace


class MyFilters:
    @staticmethod
    def init_app(app):
        app.template_filter('encode')(MyFilters.encode)
        app.template_filter('language_options')(MyFilters.language_options)

    @staticmethod
    def language_options(template):
        languages_sorted = sorted(languages_ace.items())
        return ''.join([template.format(language_value='"%s"'%val,language_name='"%s"'%key) for key,val in languages_sorted])

    @staticmethod
    def encode(text,how):
        if how == "base64":
            return base64.b64encode(text)
        elif how == "hex":
            return "".join(["\\x%02x"%(ord(c),)for c in text])