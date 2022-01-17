from django.contrib import admin
from django.utils.html import format_html
from .models import keyword_select, progress_state, keyword_visualizer
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from operator import itemgetter, attrgetter




class keyword_selectAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'author_id', 'updated_date', 'pos_text', 'neg_text', 'pos_keyword', 'neg_keyword']
    list_filter = ('user_id', ('updated_date', DateRangeFilter),)
    search_fields = ['author_id', 'pos_text', 'neg_text']


class progress_stateAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'latest_update', 'max_rand_order', 'cnt', 'current_progress']


@admin.register(keyword_visualizer)
class keyword_visualizerAdmin(admin.ModelAdmin):
    change_list_template = 'admin/keyword_visualizer_change_list.html'
    show_full_result_count = False

    list_filter = (
        'user_id',
    )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        response.context_data['pos_keyword'] = qs.values('pos_keyword').exclude(pos_keyword__isnull=True)
        a = response.context_data['pos_keyword']
        list = []

        for i in a:
            for val in i.values():
                b = list.append(val)
                a = list

        a = ' '.join(a)
        a = a.split()

        pos_keyword_dict = {}

        for i in a:
            if i in pos_keyword_dict:
                pos_keyword_dict[i] = pos_keyword_dict[i] + 1

            else:
                pos_keyword_dict[i] = 1

        pos_keyword_sorted = [(k, v) for k, v in pos_keyword_dict.items()]
        pos_keyword_sorted = sorted(pos_keyword_sorted, key=itemgetter(0))
        pos_keyword_sorted = sorted(pos_keyword_sorted, key=itemgetter(1), reverse=True)

        if pos_keyword_sorted == []:
            high = 0
        else :
            high = pos_keyword_sorted[0][1]
        low = 0

        response.context_data['pos_keywords'] = [{
            'keyword': pos_keyword_sorted[x][0],
            'recu': pos_keyword_sorted[x][1] or 0,
            'pct': \
                ((pos_keyword_sorted[x][1] or 0) - low) / (high - low) * 100
                if high > low else 0,
        } for x in range(len(pos_keyword_sorted[0:50]))]


        response.context_data['neg_keyword'] = qs.values('neg_keyword').exclude(neg_keyword__isnull=True)
        a = response.context_data['neg_keyword']
        list = []

        for i in a:
            for val in i.values():
                b = list.append(val)
                a = list

        a = ' '.join(a)
        a = a.split()

        neg_keyword_dict = {}

        for i in a:
            if i in neg_keyword_dict:
                neg_keyword_dict[i] = neg_keyword_dict[i] + 1

            else:
                neg_keyword_dict[i] = 1

        neg_keyword_sorted = [(k, v) for k, v in neg_keyword_dict.items()]
        neg_keyword_sorted = sorted(neg_keyword_sorted, key=itemgetter(0))
        neg_keyword_sorted = sorted(neg_keyword_sorted, key=itemgetter(1), reverse=True)

        if neg_keyword_sorted == []:
            high = 0
        else :
            high = neg_keyword_sorted[0][1]
        low = 0

        response.context_data['neg_keywords'] = [{
            'keyword': neg_keyword_sorted[x][0],
            'recu': neg_keyword_sorted[x][1],
            'pct': \
                ((neg_keyword_sorted[x][1]) - low) / (high - low) * 100
                if high > low else 0,
        } for x in range(len(neg_keyword_sorted[0:50]))]


        return response









admin.site.register(keyword_select, keyword_selectAdmin)
admin.site.register(progress_state, progress_stateAdmin)



