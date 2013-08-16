from crispy_forms import helper
from crispy_forms import layout
from django import forms
from django.views import generic


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
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        self.helper.add_input(layout.Submit('submit', 'Submit'))
        super(ExampleForm, self).__init__(*args, **kwargs)


class MainView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['form'] = ExampleForm()
        return context
