import os
from django.views import generic
from jsonview import decorators
import settings
from vis.models import indexed_piece


@decorators.json_view
def import_files(request):
    filepaths = [os.path.join(settings.TEST_CORPUS_PATH, fname)
                 for fname in request.GET.getlist('filenames[]')]
    indexed_pcs = [indexed_piece.IndexedPiece(fpath) for fpath in filepaths]
    return 200, [
        {"Path": ind_pc.metadata('pathname'),
         "Title": ind_pc.metadata('title'),
         "Part Names": ind_pc.metadata('parts'),
         "Offset": [0.5],
         "Part Combinations": '(none selected)',
         "Repeat Identical": False}
        for ind_pc in indexed_pcs
    ]


class MainView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context
