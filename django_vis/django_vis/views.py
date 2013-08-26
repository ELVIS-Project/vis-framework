from crispy_forms import helper, layout, bootstrap
from django import forms
from django.views import generic
from jsonview import decorators
import settings


class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label='Do you like this website?',
        choices=((1, 'Yes'), (0, 'No')),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=True
    )

    favourite_food = forms.CharField(
        label='What is your favourite food?',
        max_length=80,
        required=True
    )

    favourite_colour = forms.CharField(
        label='What is your favourite colour?',
        max_length=80,
        required=True
    )

    favourite_number = forms.IntegerField(
        label='Favourite number',
        required=False
    )

    notes = forms.CharField(
        label='Additional notes or feedback',
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.helper = helper.FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.layout = layout.Layout(
            bootstrap.TabHolder(
                bootstrap.Tab(
                    'Import',
                    'like_website',
                    layout.Div('favourite_food')
                ),
                bootstrap.Tab(
                    'working',
                    css_class='next-button'
                ),
                bootstrap.Tab(
                    'Analyze',
                    layout.Field('favourite_colour', css_class='extra')
                ),
                bootstrap.Tab(
                    'working',
                    css_class='next-button'
                ),
                bootstrap.Tab(
                    'Experiment',
                    layout.Field('favourite_number')
                ),
                bootstrap.Tab(
                    'About',
                    'notes',
                    css_class='secondary-nav'
                )
            )
        )
        super(ExampleForm, self).__init__(*args, **kwargs)


class MainView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context


@decorators.json_view
def bob(request):
    return {'success': True}
