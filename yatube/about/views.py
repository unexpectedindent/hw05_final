from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Shown page wih info about author."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Shown page wih info about techs."""
    template_name = 'about/tech.html'
