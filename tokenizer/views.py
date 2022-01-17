from konlpy.tag import Kkma
from operator import itemgetter
import math
from .models import keyword_select, user_data, user_experience
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.core import serializers
import json

from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
from django.db import connection




def keyword_selector(request):


    # 로그인 체크
    if not request.user.is_authenticated:
        # 로그인되지 않았다면 login 페이지로 redirect
        return redirect('login')
    # user_id가 ''이면 logout
    elif request.session.get('user_id', '') == '':
        return redirect('logout')
    # 로그인 되어있음
    else:
        None

    user_id = request.session.get('user_id', '').lower()
    #user_id = request.POST.get('input_user_id', '')
    next_type = request.POST.get('next_type', '')
    rand_order = request.POST.get('rand_order', '1')
    user_key = request.POST.get('user_key', '')
    id = request.POST.get('id', '')
    rand_order = int(rand_order)
    progress = 0

    if user_id != '':

        sql3 = """ select a.id, b.cnt as user_key, b.max_rand_order as rand_order from emotions.tokenizer_keyword_select a
                   inner join(select max(id) as b_id, count(*) as cnt, coalesce(max(rand_order), 0) as max_rand_order
                             from emotions.tokenizer_keyword_select where user_id = '""" + user_id + """') b
                    on a.id = b.b_id"""


        progress = keyword_select.objects.raw(sql3)
        progress = serializers.serialize('json', progress, ensure_ascii=False)
        progress = json.loads(progress)[0]['fields']
        progress['cnt'] = progress['user_key']
        progress['max_rand_order'] = progress['rand_order']
        total = progress['cnt']
        progress = progress['max_rand_order']
        max_rand_order = progress


        if progress == None:
            progress = 0

        else:
            progress = progress
            progress = (progress / total) * 100
            progress = round(progress,2)

        if next_type == 'next':

            upsert_sql = """insert into emotions.tokenizer_progress_state (user_id, latest_update, cnt, max_rand_order, progress) 
                            values ('""" + user_id + """', now(), """ + str(total) + """, """ + str(max_rand_order) + """, '""" + str(progress) + """') on duplicate key update 
                            latest_update = now(), cnt = """ + str(total) + """, max_rand_order = """ + str(max_rand_order) + """, progress = '""" + str(progress) + """'"""

            with connection.cursor() as cursor:
                cursor.execute(upsert_sql)

            sql1 = """select * from tokenizer_keyword_select
                   where user_id = '""" + user_id + """'
                   order by rand_order desc limit 1"""

            sql2 = """select * from tokenizer_keyword_select
                   where user_id = '""" + user_id + """'
                   and rand_order = """ + str(rand_order)

            data1 = keyword_select.objects.raw(sql1)
            data1 = serializers.serialize('json', data1, ensure_ascii=False)
            data1 = json.loads(data1)[0]['pk']
            data2 = keyword_select.objects.raw(sql2)
            data2 = serializers.serialize('json', data2, ensure_ascii=False)
            data2 = json.loads(data2)[0]['pk']

            if data1 == data2:
                sql = """select * 
                      from tokenizer_keyword_select 
                      where user_id = '""" + user_id + """'
                      and (pos_keyword is null or neg_keyword is null)
                      order by rand()
                      limit 1"""
            else:
                plus_number = '1'

                sql = """select * 
                      from tokenizer_keyword_select 
                      where user_id = '""" + user_id + """'
                      and rand_order = '""" + str(rand_order) + """'+'""" + plus_number + """' 
                      limit 1"""

        elif next_type == 'previous':
            if rand_order == 1:
                minus_number = '0'
            else:
                minus_number = '1'

                sql = """select *
                         from tokenizer_keyword_select 
                         where user_id = '""" + user_id + """' 
                         and rand_order = '""" + str(rand_order) + """'-'""" + minus_number + """' 
                         limit 1"""

        else:

            sql = """select *
                     from tokenizer_keyword_select
                     where user_id = '""" + user_id + """'
                     order by coalesce(rand_order, rand()) desc 
                     limit 1"""

        data = keyword_select.objects.raw(sql)
        data = serializers.serialize('json', data, ensure_ascii=False)
        data_pk = json.loads(data)[0]['pk']
        data = json.loads(data)[0]['fields']
        data['id'] = data_pk

        if next_type == 'next':
            table = keyword_select.objects.get(id=int(data['id']))
            table.updated_date = timezone.now()
            table.rand_order = rand_order + 1
            table.save()
            data['rand_order'] = str(rand_order + 1)

        if next_type == 'previous':
            table = keyword_select.objects.get(id=int(data['id']))
            table.updated_date = timezone.now()
            table.rand_order = rand_order - 1
            table.save()
            data['rand_order'] = str(rand_order - 1)

        # 완전 처음 모든 rand_order가 null일 때
        if data['rand_order'] is None:
            table = keyword_select.objects.get(id=int(data['id']))
            table.updated_date = timezone.now()
            table.rand_order = 1
            table.save()
            data['rand_order'] = '1'


        for key, val in data.items():
            if val is None:
                data[key] = ''

        data['pos_text_norm_edited_split'] = data['pos_text_norm_edited'].split(' ')
        data['neg_text_norm_edited_split'] = data['neg_text_norm_edited'].split(' ')
        data['pos_text_norm_split'] = data['pos_text_norm'].split(' ')
        data['neg_text_norm_split'] = data['neg_text_norm'].split(' ')
        data['pos_keyword_split'] = data['pos_keyword'].split(' ')
        data['neg_keyword_split'] = data['neg_keyword'].split(' ')
        data['pos_word_num_split'] = [int(x) for x in data['pos_word_num'].split(' ') if x != '']
        data['neg_word_num_split'] = [int(x) for x in data['neg_word_num'].split(' ') if x != '']


        sql_char = user_data.objects.values_list('user_id', 'agree_1', 'agree_2', 'agree_3', 'con_1', 'con_2', 'con_3',
                                                 'extra_1R', 'extra_2', 'extra_3', 'neuro_1', 'neuro_2', 'neuro_3',
                                                 'op_1', 'op_2', 'op_3')

        users_char = []

        for i in sql_char:
            if i[0] == user_id:
                this_user_char = i
            else:
                users_char.append(i)
        if user_id not in sql_char[:][0]:
            this_user_char = [0]*17

        print("this:",this_user_char)

        similarity = {}
        for i in users_char:
            rmse_list = []
            similarity['%s' % i[0]] = float

            for val in range(1, 16):
                rmse = (float(this_user_char[val]) - float(i[val])) / 5
                rmse_list.append(rmse)

            rmse = 1 - (math.sqrt((sum(list(map(lambda x: (x ** 2), rmse_list)))) / 15))
            similarity['%s' % i[0]] = rmse

        similarity_max = sorted(similarity.items(), key=itemgetter(1), reverse=True)[0][0]
        char_similarity = sorted(similarity.items(), key=itemgetter(1), reverse=True)[0][1]

        sim_user_pos_keyword = keyword_select.objects.values('pos_keyword').filter(user_id=similarity_max).exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in sim_user_pos_keyword:
            for val in i.values():
                list1.append(val)
                sim_user_pos_keyword = list1

        sim_pos_keyword = ' '.join(sim_user_pos_keyword)
        sim_pos_keyword = sim_pos_keyword.split()

        sim_pos_keyword_dict = {}

        for i in sim_pos_keyword:
            if i in sim_pos_keyword_dict:
                sim_pos_keyword_dict[i] = sim_pos_keyword_dict[i] + 1

            else:
                sim_pos_keyword_dict[i] = 1

        sim_pos_keyword = [(k, v) for k, v in sim_pos_keyword_dict.items()]
        sim_pos_keyword = sorted(sim_pos_keyword, key=itemgetter(0))
        sim_pos_keyword = sorted(sim_pos_keyword, key=itemgetter(1), reverse=True)
        sim_pos_keyword_sorted = []

        for i in range(len(sim_pos_keyword)):
            sim_pos_keyword_sorted.append(sim_pos_keyword[i][0])


        sim_pos_keyword_value = []
        sim_pos_keyword_n = []


        for i in range(50):
            if sim_pos_keyword != []:
                sim_pos_keyword_value.append(sim_pos_keyword[i][0])
                sim_pos_keyword_n.append(sim_pos_keyword[i][1])


        sim_pos_rec_value = []

        for i in sim_pos_keyword_value:
            if len(sim_pos_rec_value) == 5:
                break
            elif i in data['pos_text_norm_split']:
                sim_pos_rec_value.append(i)

        sim_pos_rec_n=[]

        for i in sim_pos_rec_value:
            if i in sim_pos_keyword_value:
                sim_pos_rec_n.append(sim_pos_keyword_n[(sim_pos_keyword_value.index(i))])

        if sim_pos_keyword_n != []:
            sim_pos_rec_max = max(sim_pos_keyword_n)
            sim_pos_all_per = []

        if sim_pos_keyword_n != []:
            for i in sim_pos_keyword_n:
                if i == 0:
                    percentage = ((1/sim_pos_rec_max)*100)
                    sim_pos_all_per.append(percentage)
                else:
                    percentage = ((i/sim_pos_rec_max)*100)
                    sim_pos_all_per.append(percentage)
        else:
            sim_pos_all_per = 0

        number = 0
        sim_pos_fullrange = []
        for i in range(len(sim_pos_keyword_n)):
            sim_pos_fullrange.append(number)
            number = number + 1



        all_pos_keyword = keyword_select.objects.values('pos_keyword').exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in all_pos_keyword:
            for val in i.values():
                list1.append(val)
                all_pos_keyword = list1

        all_pos_keyword = ' '.join(all_pos_keyword)
        all_pos_keyword = all_pos_keyword.split()

        all_pos_keyword_dict = {}
        for i in all_pos_keyword:
            if i in all_pos_keyword_dict:
                all_pos_keyword_dict[i] = all_pos_keyword_dict[i] + 1

            else:
                all_pos_keyword_dict[i] = 1

        all_pos_keyword = [(k, v) for k, v in all_pos_keyword_dict.items()]
        all_pos_keyword = sorted(all_pos_keyword, key=itemgetter(0))
        all_pos_keyword = sorted(all_pos_keyword, key=itemgetter(1), reverse=True)

        all_pos_keyword_value = []
        all_pos_keyword_n = []

        for i in range(50):
            all_pos_keyword_value.append(all_pos_keyword[i][0])
            all_pos_keyword_n.append(all_pos_keyword[i][1])


        all_pos_rec_value = []

        for i in all_pos_keyword_value:
            if len(all_pos_rec_value) == 5:
                break
            elif i in data['pos_text_norm_split']:
                all_pos_rec_value.append(i)

        all_pos_rec_n=[]

        for i in all_pos_rec_value:
            if i in all_pos_keyword_value:
                all_pos_rec_n.append(all_pos_keyword_n[(all_pos_keyword_value.index(i))])


        all_pos_rec_max = max(all_pos_keyword_n)
        all_pos_all_per = []

        for i in all_pos_keyword_n:
            if i == 0:
                percentage = ((1/all_pos_rec_max)*100)
                all_pos_all_per.append(percentage)
            else:
                percentage = ((i/all_pos_rec_max)*100)
                all_pos_all_per.append(percentage)

        number = 0
        all_pos_fullrange = []
        for i in range(len(all_pos_keyword_n)):
            all_pos_fullrange.append(number)
            number = number + 1


        sql_pos_keyword = keyword_select.objects.values('pos_keyword').filter(user_id=user_id).exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in sql_pos_keyword:
            for val in i.values():
                list1.append(val)
                sql_pos_keyword = list1

        pos_keyword = ' '.join(sql_pos_keyword)
        pos_keyword = pos_keyword.split()

        pos_keyword_dict = {}

        for i in pos_keyword:
            if i in pos_keyword_dict:
                pos_keyword_dict[i] = pos_keyword_dict[i] + 1

            else:
                pos_keyword_dict[i] = 1

        pos_keyword = [(k, v) for k, v in pos_keyword_dict.items()]
        pos_keyword = sorted(pos_keyword, key=itemgetter(0))
        pos_keyword = sorted(pos_keyword, key=itemgetter(1), reverse=True)
        pos_keyword_sorted = []

        for i in range(len(pos_keyword)):
            pos_keyword_sorted.append(pos_keyword[i][0])

        pos_keyword_value = []
        pos_keyword_n = []
        print("pos_keyword:",pos_keyword)
        if pos_keyword != []:
            for i in range(50):
                if i <= (len(pos_keyword) - 1):
                    pos_keyword_value.append(pos_keyword[i][0])
                    pos_keyword_n.append(pos_keyword[i][1])

        pos_rec_value = []

        for i in pos_keyword_value:
            if len(pos_rec_value) == 5:
                break
            elif i in data['pos_text_norm_split']:
                pos_rec_value.append(i)

        pos_keyword_rec=[]


        for i in all_pos_keyword_value:
            if len(pos_keyword_rec) < 1:
                if i in data['pos_text_norm_split']:
                    pos_keyword_rec.append(data['pos_text_norm_split'].index(i)+1)
                    print(pos_keyword_rec)


        for i in pos_keyword_value:
            if len(pos_keyword_rec) < 2:
                if i in data['pos_text_norm_split'] and (data['pos_text_norm_split'].index(i) + 1) not in pos_keyword_rec:
                    pos_keyword_rec.append(data['pos_text_norm_split'].index(i) + 1)


        for i in sim_pos_keyword_value:
            if len(pos_keyword_rec) < 3:
                if i in data['pos_text_norm_split'] and (data['pos_text_norm_split'].index(i) + 1 ) not in pos_keyword_rec:
                    pos_keyword_rec.append(data['pos_text_norm_split'].index(i) + 1)


        pos_rec_n=[]

        for i in pos_rec_value:
            if i in pos_keyword_value:
                pos_rec_n.append(pos_keyword_n[(pos_keyword_value.index(i))])


        if pos_keyword_n != []:
            pos_rec_max = max(pos_keyword_n)
        pos_all_per = []

        for i in pos_keyword_n:
            if i == 0:
                percentage = ((1/pos_rec_max)*100)
                pos_all_per.append(percentage)
            else:
                percentage = ((i/pos_rec_max)*100)
                pos_all_per.append(percentage)

        number = 0
        pos_fullrange = []
        for i in range(len(pos_keyword_n)):
            pos_fullrange.append(number)
            number = number + 1


         #negative
        sim_user_neg_keyword = keyword_select.objects.values('neg_keyword').filter(user_id=similarity_max).exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in sim_user_neg_keyword:
            for val in i.values():
                list1.append(val)
                sim_user_neg_keyword = list1

        sim_neg_keyword = ' '.join(sim_user_neg_keyword)
        sim_neg_keyword = sim_neg_keyword.split()

        sim_neg_keyword_dict = {}

        for i in sim_neg_keyword:
            if i in sim_neg_keyword_dict:
                sim_neg_keyword_dict[i] = sim_neg_keyword_dict[i] + 1

            else:
                sim_neg_keyword_dict[i] = 1

        sim_neg_keyword = [(k, v) for k, v in sim_neg_keyword_dict.items()]
        sim_neg_keyword = sorted(sim_neg_keyword, key=itemgetter(0))
        sim_neg_keyword = sorted(sim_neg_keyword, key=itemgetter(1), reverse=True)
        sim_neg_keyword_sorted = []

        for i in range(len(sim_neg_keyword)):
            sim_neg_keyword_sorted.append(sim_neg_keyword[i][0])


        sim_neg_keyword_value = []
        sim_neg_keyword_n = []


        if sim_neg_keyword != []:
            for i in range(50):
                sim_neg_keyword_value.append(sim_neg_keyword[i][0])
                sim_neg_keyword_n.append(sim_neg_keyword[i][1])


        sim_neg_rec_value = []

        for i in sim_neg_keyword_value:
            if len(sim_neg_rec_value) == 5:
                break
            elif i in data['neg_text_norm_split']:
                sim_neg_rec_value.append(i)

        sim_neg_rec_n=[]

        for i in sim_neg_rec_value:
            if i in sim_neg_keyword_value:
                sim_neg_rec_n.append(sim_neg_keyword_n[(sim_neg_keyword_value.index(i))])

        if sim_neg_keyword_n != []:
            sim_neg_rec_max = max(sim_neg_keyword_n)
            sim_neg_all_per = []

        if sim_neg_keyword_n != []:
            for i in sim_neg_keyword_n:
                if i == 0:
                    percentage = ((1/sim_neg_rec_max)*100)
                    sim_neg_all_per.append(percentage)
                else:
                    percentage = ((i/sim_neg_rec_max)*100)
                    sim_neg_all_per.append(percentage)
        else:
            sim_neg_all_per = 0

        number = 0
        sim_neg_fullrange = []
        for i in range(len(sim_neg_keyword_n)):
            sim_neg_fullrange.append(number)
            number = number + 1



        all_neg_keyword = keyword_select.objects.values('neg_keyword').exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in all_neg_keyword:
            for val in i.values():
                list1.append(val)
                all_neg_keyword = list1

        all_neg_keyword = ' '.join(all_neg_keyword)
        all_neg_keyword = all_neg_keyword.split()

        all_neg_keyword_dict = {}
        for i in all_neg_keyword:
            if i in all_neg_keyword_dict:
                all_neg_keyword_dict[i] = all_neg_keyword_dict[i] + 1

            else:
                all_neg_keyword_dict[i] = 1

        all_neg_keyword = [(k, v) for k, v in all_neg_keyword_dict.items()]
        all_neg_keyword = sorted(all_neg_keyword, key=itemgetter(0))
        all_neg_keyword = sorted(all_neg_keyword, key=itemgetter(1), reverse=True)

        all_neg_keyword_value = []
        all_neg_keyword_n = []

        for i in range(50):
            all_neg_keyword_value.append(all_neg_keyword[i][0])
            all_neg_keyword_n.append(all_neg_keyword[i][1])


        all_neg_rec_value = []

        for i in all_neg_keyword_value:
            if len(all_neg_rec_value) == 5:
                break
            elif i in data['neg_text_norm_split']:
                all_neg_rec_value.append(i)

        all_neg_rec_n=[]

        for i in all_neg_rec_value:
            if i in all_neg_keyword_value:
                all_neg_rec_n.append(all_neg_keyword_n[(all_neg_keyword_value.index(i))])


        all_neg_rec_max = max(all_neg_keyword_n)
        all_neg_all_per = []

        for i in all_neg_keyword_n:
            if i == 0:
                percentage = ((1/all_neg_rec_max)*100)
                all_neg_all_per.append(percentage)
            else:
                percentage = ((i/all_neg_rec_max)*100)
                all_neg_all_per.append(percentage)

        number = 0
        all_neg_fullrange = []
        for i in range(len(all_neg_keyword_n)):
            all_neg_fullrange.append(number)
            number = number + 1


        sql_neg_keyword = keyword_select.objects.values('neg_keyword').filter(user_id=user_id).exclude(
            pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)

        list1 = []

        for i in sql_neg_keyword:
            for val in i.values():
                list1.append(val)
                sql_neg_keyword = list1

        neg_keyword = ' '.join(sql_neg_keyword)
        neg_keyword = neg_keyword.split()

        neg_keyword_dict = {}

        for i in neg_keyword:
            if i in neg_keyword_dict:
                neg_keyword_dict[i] = neg_keyword_dict[i] + 1

            else:
                neg_keyword_dict[i] = 1

        neg_keyword = [(k, v) for k, v in neg_keyword_dict.items()]
        neg_keyword = sorted(neg_keyword, key=itemgetter(0))
        neg_keyword = sorted(neg_keyword, key=itemgetter(1), reverse=True)
        neg_keyword_sorted = []

        for i in range(len(neg_keyword)):
            neg_keyword_sorted.append(neg_keyword[i][0])

        neg_keyword_value = []
        neg_keyword_n = []

        print("neg_keyword:",neg_keyword)

        if neg_keyword != []:
            for i in range(50):
                if i <= (len(neg_keyword) - 1):
                    neg_keyword_value.append(neg_keyword[i][0])
                    neg_keyword_n.append(neg_keyword[i][1])

        neg_rec_value = []

        for i in neg_keyword_value:
            if len(neg_rec_value) == 5:
                break
            elif i in data['neg_text_norm_split']:
                neg_rec_value.append(i)


        neg_rec_n=[]

        for i in neg_rec_value:
            if i in neg_keyword_value:
                neg_rec_n.append(neg_keyword_n[(neg_keyword_value.index(i))])


        if neg_keyword_n != []:
            neg_rec_max = max(neg_keyword_n)
        neg_all_per = []

        for i in neg_keyword_n:
            if i == 0:
                percentage = ((1/neg_rec_max)*100)
                neg_all_per.append(percentage)
            else:
                percentage = ((i/neg_rec_max)*100)
                neg_all_per.append(percentage)

        number = 0
        neg_fullrange = []
        for i in range(len(neg_keyword_n)):
            neg_fullrange.append(number)
            number = number + 1


        neg_keyword_rec=[]

        for i in all_neg_keyword_value:
            if len(neg_keyword_rec) < 1:
                if i in data['neg_text_norm_split']:
                    neg_keyword_rec.append(data['neg_text_norm_split'].index(i)+1)


        for i in neg_keyword_value:
            if len(neg_keyword_rec) < 2:
                if i in data['neg_text_norm_split'] and (data['neg_text_norm_split'].index(i) + 1) not in neg_keyword_rec:
                    neg_keyword_rec.append(data['neg_text_norm_split'].index(i) + 1)


        for i in sim_neg_keyword_value:
            if len(neg_keyword_rec) < 3:
                if i in data['neg_text_norm_split'] and (data['neg_text_norm_split'].index(i) + 1 ) not in neg_keyword_rec:
                    neg_keyword_rec.append(data['neg_text_norm_split'].index(i) + 1)

        print("pos_keyword_value:",pos_keyword_value)

    else:
        data = dict()
        data['rand_order'] = 1

    if request.method == "POST":
        print("POST requested")

        # if method == POST and submit name == submit_upload, insert csv file to database
        if 'submit_user_id' in request.POST:
            print("submit_user_id")
            print(request.POST.get('input_user_id', ''))

    content = {'user_id':user_id, 'data':data, 'progress':progress, 'total':total, 'max_rand_order':max_rand_order,
               'pos_keyword_rec':pos_keyword_rec, 'pos_keyword_n':pos_keyword_n,'pos_keyword_value':pos_keyword_value,
               'pos_rec_value':pos_rec_value, 'pos_rec_n':pos_rec_n, 'pos_all_per':pos_all_per,
               'pos_fullrange': pos_fullrange,'all_pos_keyword_value':all_pos_keyword_value,
               'all_pos_keyword_n':all_pos_keyword_n,'sim_pos_keyword_value':sim_pos_keyword_value,
               'sim_pos_keyword_n':sim_pos_keyword_n, 'sim_pos_rec_value':sim_pos_rec_value,
               'sim_pos_all_per':sim_pos_all_per,'sim_pos_fullrange':sim_pos_fullrange,
               'all_pos_rec_value':all_pos_rec_value,'all_pos_all_per': all_pos_all_per,
               'all_pos_fullrange':all_pos_fullrange,'neg_keyword_rec': neg_keyword_rec, 'neg_keyword_n': neg_keyword_n,
               'neg_keyword_value': neg_keyword_value,'neg_rec_value': neg_rec_value, 'neg_rec_n': neg_rec_n,
               'neg_all_per': neg_all_per,'neg_fullrange': neg_fullrange,'all_neg_keyword_value': all_neg_keyword_value,
               'all_neg_keyword_n': all_neg_keyword_n,'sim_neg_keyword_value': sim_neg_keyword_value,
               'sim_neg_keyword_n': sim_neg_keyword_n, 'sim_neg_rec_value': sim_neg_rec_value,
               'sim_neg_all_per': sim_neg_all_per, 'sim_neg_fullrange': sim_neg_fullrange,
               'all_neg_rec_value': all_neg_rec_value, 'all_neg_all_per': all_neg_all_per,
               'all_neg_fullrange': all_neg_fullrange,'similarity_max':similarity_max, 'char_similarity':char_similarity
               }

    return render(request, 'tokenizer/keyword_selector.html', content)




def keyword_selector_update_edit(request):

    # 로그인 체크
    if not request.user.is_authenticated:
        print("Not logged in")
        # 로그인되지 않았다면 login 페이지로 redirect
        return redirect('login')
    # user_id가 ''이면 logout
    elif request.session.get('user_id', '') == '':
        return redirect('logout')
    # 로그인 되어있음
    else:
        print("Logged in")
        print(request.session.get('user_id', ''))

    user_id = request.GET.get('user_id').lower()
    user_key = request.GET.get('user_key')
    id = request.GET.get('id')
    type = request.GET.get('type')
    text_norm = request.GET.get('text_norm')
    if text_norm == '':
        text_norm = None
    table = keyword_select.objects.get(id=id)
    table.updated_date = timezone.now()
    if type == "positive_words":
        table.pos_text_norm_edited = text_norm
        table.pos_keyword = None
        table.pos_word_num = None
    elif type == "negative_words":
        table.neg_text_norm_edited = text_norm
        table.neg_keyword = None
        table.neg_word_num = None

    table.save()

    return HttpResponse("Success!")


def keyword_selector_update(request):

    # 로그인 체크
    if not request.user.is_authenticated:
        print("Not logged in")
        # 로그인되지 않았다면 login 페이지로 redirect
        return redirect('login')
    # user_id가 ''이면 logout
    elif request.session.get('user_id', '') == '':
        return redirect('logout')
    # 로그인 되어있음
    else:
        print("Logged in")
        print(request.session.get('user_id', ''))

    user_id = request.GET.get('user_id').lower()
    user_key = request.GET.get('user_key')
    id = request.GET.get('id')
    type = request.GET.get('type')
    selected_keywords = request.GET.get('selected_keywords')
    selected_keywords_order = request.GET.get('selected_keywords_order')

    table = keyword_select.objects.get(id=id)
    table.updated_date = timezone.now()
    if type == "positive_words":
        table.pos_keyword = selected_keywords
        table.pos_word_num = selected_keywords_order
    elif type == "negative_words":
        table.neg_keyword = selected_keywords
        table.neg_word_num = selected_keywords_order

    table.save()

    return HttpResponse("Success!")

def help(request):
    return render(request, 'tokenizer/help.html')

def pos_keyword_view(request):

    user_id = request.session.get('user_id', '').lower()

    if user_id != "":

        sql_pos_keyword = keyword_select.objects.values('pos_keyword').filter(user_id=user_id).exclude(pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)
        list = []

        for i in sql_pos_keyword:
            for val in i.values():
                list.append(val)
                sql_pos_keyword = list

        pos_keyword = ' '.join(sql_pos_keyword)
        pos_keyword = pos_keyword.split()

        pos_keyword_dictio = {}

        for i in pos_keyword:
            if i in pos_keyword_dictio:
                pos_keyword_dictio[i] = pos_keyword_dictio[i] + 1

            else:
                pos_keyword_dictio[i] = 1

        sql = """select *
                 from tokenizer_keyword_select
                 where user_id = '""" + user_id + """'
                 order by rand_order desc 
                 limit 1"""

        data = keyword_select.objects.raw(sql)
        data = serializers.serialize('json', data, ensure_ascii=False)
        data_pk = json.loads(data)[0]['pk']
        data = json.loads(data)[0]['fields']
        data['id'] = data_pk
        data['pos_text_norm_split'] = data['pos_text_norm'].split(' ')

        pos_keyword = [ (k, v) for k, v in pos_keyword_dictio.items()]
        pos_keyword = sorted(pos_keyword, key=itemgetter(0))
        pos_keyword = sorted(pos_keyword, key=itemgetter(1), reverse=True)

        pos_keyword_value = []
        pos_keyword_n = []

        for i in range(len(pos_keyword)):
            pos_keyword_value.append(pos_keyword[i][0])
            pos_keyword_n.append(pos_keyword[i][1])



        pos_rec_value = []

        for i in pos_keyword_value:
            if len(pos_rec_value) == 5:
                break
            elif i in data['pos_text_norm_split']:
                pos_rec_value.append(i)


        pos_all_value = []

        for i in data['pos_text_norm_split']:
            if i not in pos_all_value:
                pos_all_value.append(i)


        pos_rec_n=[]

        for i in pos_rec_value:
            if i in pos_keyword_value:
                pos_rec_n.append(pos_keyword_n[(pos_keyword_value.index(i))])



        pos_all_n=[]

        for i in pos_all_value:
            if i in pos_keyword_value:
                pos_all_n.append(pos_keyword_n[(pos_keyword_value.index(i))])
            elif i not in pos_keyword_value:
                pos_all_n.append(0)



        pos_rec_max = max(pos_rec_n)
        pos_all_per = []

        for i in pos_all_n:
            if i == 0:
                percentage = ((1/pos_rec_max)*100)
                pos_all_per.append(percentage)
            else:
                percentage = ((i/pos_rec_max)*100)
                pos_all_per.append(percentage)
        print(pos_keyword)
        print(pos_rec_max)
        print(pos_all_per)
        print(pos_all_value)
        print(pos_rec_value)
        print(pos_all_n)
        print(pos_rec_n)

        number = 0
        fullrange = []
        for i in range(len(pos_all_n)):
            fullrange.append(number)
            number = number + 1


    content = {'pos_rec_max':pos_rec_max, 'pos_rec_value':pos_rec_value, 'pos_rec_n':pos_rec_n,
               'pos_all_per':pos_all_per, 'pos_all_value':pos_all_value, 'pos_all_n':pos_all_n, 'fullrange': fullrange}

    return render(request, 'tokenizer/pos_keyword_view.html', content)

def neg_keyword_view(request):

    user_id = request.session.get('user_id', '').lower()

    if user_id != "":

        sql_pos_keyword = keyword_select.objects.values('neg_keyword').filter(user_id=user_id).exclude(pos_keyword__isnull=True).exclude(neg_keyword__isnull=True)
        list = []

        for i in sql_pos_keyword:
            for val in i.values():
                list.append(val)
                sql_pos_keyword = list

        pos_keyword = ' '.join(sql_pos_keyword)
        pos_keyword = pos_keyword.split()

        pos_keyword_dictio = {}

        for i in pos_keyword:
            if i in pos_keyword_dictio:
                pos_keyword_dictio[i] = pos_keyword_dictio[i] + 1

            else:
                pos_keyword_dictio[i] = 1

        sql = """select *
                 from tokenizer_keyword_select
                 where user_id = '""" + user_id + """'
                 order by rand_order desc 
                 limit 1"""

        data = keyword_select.objects.raw(sql)
        data = serializers.serialize('json', data, ensure_ascii=False)
        data_pk = json.loads(data)[0]['pk']
        data = json.loads(data)[0]['fields']
        data['id'] = data_pk
        data['neg_text_norm_split'] = data['neg_text_norm'].split(' ')

        pos_keyword = [ (k, v) for k, v in pos_keyword_dictio.items()]
        pos_keyword = sorted(pos_keyword, key=itemgetter(0))
        pos_keyword = sorted(pos_keyword, key=itemgetter(1), reverse=True)

        pos_keyword_value = []
        pos_keyword_n = []

        for i in range(len(pos_keyword)):
            pos_keyword_value.append(pos_keyword[i][0])
            pos_keyword_n.append(pos_keyword[i][1])



        pos_rec_value = []

        for i in pos_keyword_value:
            if len(pos_rec_value) == 5:
                break
            elif i in data['neg_text_norm_split']:
                pos_rec_value.append(i)


        pos_all_value = []

        for i in data['neg_text_norm_split']:
            if i not in pos_all_value:
                pos_all_value.append(i)


        pos_rec_n=[]

        for i in pos_rec_value:
            if i in pos_keyword_value:
                pos_rec_n.append(pos_keyword_n[(pos_keyword_value.index(i))])



        pos_all_n=[]

        for i in pos_all_value:
            if i in pos_keyword_value:
                pos_all_n.append(pos_keyword_n[(pos_keyword_value.index(i))])
            elif i not in pos_keyword_value:
                pos_all_n.append(0)



        pos_rec_max = max(pos_rec_n)
        pos_all_per = []

        for i in pos_all_n:
            if i == 0:
                percentage = ((1/pos_rec_max)*100)
                pos_all_per.append(percentage)
            else:
                percentage = ((i/pos_rec_max)*100)
                pos_all_per.append(percentage)
        print(pos_keyword)
        print(pos_rec_max)
        print(pos_all_per)
        print(pos_all_value)
        print(pos_rec_value)
        print(pos_all_n)
        print(pos_rec_n)

        number = 0
        fullrange = []
        for i in range(len(pos_all_n)):
            fullrange.append(number)
            number = number + 1


    content = {'pos_rec_max':pos_rec_max, 'pos_rec_value':pos_rec_value, 'pos_rec_n':pos_rec_n,
               'pos_all_per':pos_all_per, 'pos_all_value':pos_all_value, 'pos_all_n':pos_all_n, 'fullrange': fullrange}

    return render(request, 'tokenizer/neg_keyword_view.html', content)

# sign up
def signup(request):
    user_id = request.POST.get('user_id', '').lower()
    name = request.POST.get('name', '')
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    mobile = request.POST.get('mobile', '')
    email = request.POST.get('email', '').lower()
    birth = request.POST.get('birth', '')
    gender = request.POST.get('gender', '')
    positive_comment = request.POST.get('positive_comment', '')
    negative_comment = request.POST.get('negative_comment', '')
    pos_emo1 = request.POST.get('pos_emo1', '')
    pos_emo1_w = request.POST.get('pos_emo1_w', '')
    pos_emo2 = request.POST.get('pos_emo2', '')
    pos_emo2_w = request.POST.get('pos_emo2_w', '')
    pos_emo3 = request.POST.get('pos_emo3', '')
    pos_emo3_w = request.POST.get('pos_emo3_w', '')
    pos_emo4 = request.POST.get('pos_emo4', '')
    pos_emo4_w = request.POST.get('pos_emo4_w', '')
    pos_emo5 = request.POST.get('pos_emo5', '')
    pos_emo5_w = request.POST.get('pos_emo5_w', '')
    neg_emo1 = request.POST.get('neg_emo1', '')
    neg_emo1_w = request.POST.get('neg_emo1_w', '')
    neg_emo2 = request.POST.get('neg_emo2', '')
    neg_emo2_w = request.POST.get('neg_emo2_w', '')
    neg_emo3 = request.POST.get('neg_emo3', '')
    neg_emo3_w = request.POST.get('neg_emo3_w', '')
    neg_emo4 = request.POST.get('neg_emo4', '')
    neg_emo4_w = request.POST.get('neg_emo4_w', '')
    neg_emo5 = request.POST.get('neg_emo5', '')
    neg_emo5_w = request.POST.get('neg_emo5_w', '')
    op_1 = request.POST.get('op_1', '')
    op_2 = request.POST.get('op_2', '')
    op_3 = request.POST.get('op_3', '')
    con_1 = request.POST.get('con_1', '')
    con_2 = request.POST.get('con_2', '')
    con_3 = request.POST.get('con_3', '')
    neuro_1 = request.POST.get('neuro_1', '')
    neuro_2 = request.POST.get('neuro_2', '')
    neuro_3 = request.POST.get('neuro_3', '')
    extra_1 = request.POST.get('extra_1', '')
    extra_2 = request.POST.get('extra_2', '')
    extra_3 = request.POST.get('extra_3', '')
    agree_1 = request.POST.get('agree_1', '')
    agree_2 = request.POST.get('agree_2', '')
    agree_3 = request.POST.get('agree_3', '')
    if extra_1 != '':
        extra_1R = 6 - int(extra_1)
        op_avg = ((int(op_1)+int(op_2)+int(op_3))/3)
        con_avg = ((int(con_1)+int(con_2)+int(con_3))/3)
        neuro_avg = ((int(neuro_1)+int(neuro_2)+int(neuro_3))/3)
        extra_avg = ((extra_1R+int(extra_2)+int(extra_3))/3)
        agree_avg = ((int(agree_1)+int(agree_2)+int(agree_3))/3)

    if request.method == "POST":

        # auth_user 테이블 유저 생성
        user = User.objects.create_user(username=user_id, password=password1)
        auth_user_pk = user.id
        # default data를 insert 하는 query 생성
        insert_sql = """insert into emotions.tokenizer_keyword_select (created_date, created_by, user_id, user_key, author_id, pos_text, neg_text, pos_text_norm, neg_text_norm)
                        select now(), 'admin', '""" + user_id + """', user_key, author_id, pos_text, neg_text, pos_text_norm, neg_text_norm
                        from emotions.default_table"""
        # default table의 데이터를 insert
        with connection.cursor() as cursor:
            cursor.execute(insert_sql)

        # 다른 유저가 입력한 데이터(tokenizer_user_experience 테이블)를 insert 하는 query 생성
        insert_sql = """insert into emotions.tokenizer_keyword_select (created_date, created_by, user_id, user_key, author_id, pos_text, neg_text, pos_text_norm, neg_text_norm)
                        select now(), created_by, '""" + user_id + """', id, created_by, pos_text, neg_text, pos_text_norm, neg_text_norm
                        from emotions.tokenizer_user_experience"""
        # tokenizer_user_experience 테이블의 데이터를 insert
        with connection.cursor() as cursor:
            cursor.execute(insert_sql)

        # tokenizer_user_data 테이블에 유저 데이터 입력
        user_data_model = user_data(auth_user_pk=auth_user_pk, user_id=user_id, user_name=name, mobile=mobile, email=email, birth=birth,
                                    gender=gender, pos_text=positive_comment, neg_text=negative_comment, pos_emo1 = pos_emo1, pos_emo1_w = pos_emo1_w,
                                    pos_emo2 = pos_emo2, pos_emo2_w = pos_emo2_w, pos_emo3 = pos_emo3, pos_emo3_w = pos_emo3_w, pos_emo4 = pos_emo4,
                                    pos_emo4_w = pos_emo4_w, pos_emo5 = pos_emo5, pos_emo5_w = pos_emo5_w, neg_emo1 = neg_emo1, neg_emo1_w = neg_emo1_w,
                                    neg_emo2 = neg_emo2, neg_emo2_w = neg_emo2_w, neg_emo3 = neg_emo3, neg_emo3_w = neg_emo3_w, neg_emo4 = neg_emo4,
                                    neg_emo4_w = neg_emo4_w, neg_emo5 = neg_emo5, neg_emo5_w = neg_emo5_w, op_1 = op_1, op_2 = op_2, op_3 = op_3,
                                    con_1 = con_1, con_2 = con_2, con_3 = con_3, neuro_1 = neuro_1, neuro_2 = neuro_2, neuro_3 = neuro_3, extra_1 = extra_1,
                                    extra_2 = extra_2, extra_3 = extra_3, agree_1 = agree_1, agree_2 = agree_2, agree_3 = agree_3, extra_1R=extra_1R, op_avg=op_avg,
                                    con_avg=con_avg, neuro_avg=neuro_avg, extra_avg=extra_avg, agree_avg=agree_avg)
        user_data_model.save()

        # 새로 생성된 유저의 tokenizer_keyword_select 테이블 데이터에서 랜덤으로 하나의 rand_order를 1로 업데이트 한다.
        update_sql = """ update emotions.tokenizer_keyword_select a,
                                (select id from emotions.tokenizer_keyword_select where user_id = '""" + user_id + """' order by rand() limit 1) b
                         set a.rand_order = 1
                         where a.id = b.id"""
        with connection.cursor() as cursor:
            cursor.execute(update_sql)

        # 로그인
        auth.login(request, user)
        # session에 username 저장
        request.session['user_id'] = user_id

        # 실행 시간이 오래 걸리는 작업은 signup_after 에서 처리한다.
        # 1. 유저가 입력한 경험 데이터에 konlpy 를 적용한다.
        # 2. tokenizer_user_experience 테이블에 유저가 입력한 경험 데이터 입력한다.
        # 3. tokenizer_user_experience 테이블에서 현재 유저의 데이터를 tokenizer_keyword_select 테이블의 모든 유저에게 insert 한다.
        content = {'auth_user_pk': auth_user_pk,
                   'user_id': user_id,
                   'positive_comment': positive_comment,
                   'negative_comment': negative_comment,
                   }
        return render(request, 'tokenizer/signup_after.html', content)


        # keyword_selector로 redirect
        #return redirect('keyword_selector')


    return render(request, 'tokenizer/signup.html', {})


# sign up 중간에 시간이 오래 걸리는 작업은 ajax로 처리한다.
def signup_after(request):
    print('signup_after')
    auth_user_pk = int(request.GET.get('auth_user_pk', '0'))
    user_id = request.GET.get('user_id', '').lower()
    positive_comment = request.GET.get('positive_comment', '')
    negative_comment = request.GET.get('negative_comment', '')

    if request.user.username != user_id:
        return HttpResponse('Fail')

    if auth_user_pk==0 or user_id == '' or positive_comment == '' or negative_comment == '':
        return HttpResponse('Fail')


    # 유저가 입력한 경험 데이터에 konlpy 적용
    kkma = Kkma()
    pos_text_norm = kkma.pos(positive_comment)
    pos_text_norm = [i[0] for i in pos_text_norm]
    pos_text_norm = ' '.join(pos_text_norm)

    neg_text_norm = kkma.pos(negative_comment)
    neg_text_norm = [i[0] for i in neg_text_norm]
    neg_text_norm = ' '.join(neg_text_norm)
    # tokenizer_user_experience 테이블에 유저가 입력한 경험 데이터 입력
    user_experience_model = user_experience(auth_user_pk=auth_user_pk, created_by=user_id, user_id=user_id,
                                            user_key=auth_user_pk, author_id=auth_user_pk,
                                            pos_text=positive_comment, neg_text=negative_comment,
                                            pos_text_norm=pos_text_norm, neg_text_norm=neg_text_norm)
    user_experience_model.save()

    # tokenizer_user_experience 테이블에서 현재 유저의 데이터를 tokenizer_keyword_select 테이블의 모든 유저에게 insert
    insert_sql = """insert into emotions.tokenizer_keyword_select (created_date, created_by, user_id, user_key, author_id, pos_text, neg_text, pos_text_norm, neg_text_norm)
                    select now(), a.created_by, b.user_id, a.id, a.created_by, a.pos_text, a.neg_text, a.pos_text_norm, a.neg_text_norm
                    from emotions.tokenizer_user_experience a
                    inner join (select distinct user_id from emotions.tokenizer_keyword_select) b
                    on 1=1
                    where a.auth_user_pk = """ + str(auth_user_pk)
    # tokenizer_user_experience 테이블의 데이터를 insert
    with connection.cursor() as cursor:
        cursor.execute(insert_sql)
    print('signup_after end')
    return HttpResponse("Success")


# user를 생성하기 전 중복되는 user_id가 있는지 체크하는 함수
# signup.html 에서 ajax를 통해 호출된다.
def user_duplication_check(request):

    error = ''
    user_id = request.GET.get('user_id').lower()
    # 동일 user id가 있는지 확인
    if User.objects.filter(username=user_id).first() is not None:
        error = '동일한 User ID가 이미 존재합니다.'
    # 현재 유저 수가 100명 이상인지 확인
    elif User.objects.count() > 100:
        error = '더 이상 계정을 만들 수 없습니다.'

    return HttpResponse(error)



# log in
def login(request):
    error = ''
    username = request.POST.get('username', '').strip().lower()
    password = request.POST.get('password', '')

    if request.method == "POST":
        # 유저가 존재하는지 확인
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            # 로그인
            auth.login(request, user)
            # 세션에 유저이름 저장
            request.session['user_id'] = username
            # keyword_selector로 redirect
            return redirect('keyword_selector')
        else:
            return render(request, 'tokenizer/login.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'tokenizer/login.html')

# log out
def logout(request):
    auth.logout(request)
    return redirect('login')



# 유저 정보 조회
def account(request):

    # 로그인 체크
    if not request.user.is_authenticated:
        # 로그인되지 않았다면 login 페이지로 redirect
        return redirect('login')
    # user_id가 ''이면 logout
    elif request.session.get('user_id', '') == '':
        return redirect('logout')
    # 로그인 되어있음
    else:
        print(request.session.get('user_id', ''))

    # 현재 유저 정보 조회
    user_id = request.session.get('user_id', '').lower()

    sql = """select * from tokenizer_user_data
           where user_id = '""" + user_id + """'
           limit 1"""
    data = user_data.objects.raw(sql)
    data = serializers.serialize('json', data, ensure_ascii=False)
    data = json.loads(data)[0]['fields']


    # GET일 경우 현재 유저의 정보를 보여준다.
    if request.method == 'GET':
        content = {'data': data}
        return render(request, 'tokenizer/account.html', content)


    # Edit 버튼을 눌렀을 경우 유저 정보를 수정한다.
    elif request.method == 'POST' and request.POST.get('action', '') == 'edit':
        user_id = request.POST.get('user_id', '').lower()
        name = request.POST.get('name', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        mobile = request.POST.get('mobile', '')
        email = request.POST.get('email', '').lower()
        birth = request.POST.get('birth', '')
        gender = request.POST.get('gender', '')
        positive_comment = request.POST.get('positive_comment', '')
        negative_comment = request.POST.get('negative_comment', '')

        # tokenizer_user_data 테이블에서 유저 정보를 가져온다.
        table = user_data.objects.get(user_id=user_id)
        table.updated_date = timezone.now()
        table.user_name = name
        table.mobile = mobile
        table.email = email
        table.birth = birth
        table.birth = birth
        table.gender = gender
        table.save()

        # 만약 비밀번호가 수정되었다면 auth_user 테이블의 유저 비밀번호를 변경한다.
        if request.POST.get('password_is_edited', 'false') == 'true':
            user = request.user
            user.set_password(password1)
            user.save()
            auth.login(request, user)


        return redirect('keyword_selector')


    # delete account 버튼을 눌렀을 경우 유저를 삭제한다.
    elif request.method == 'POST' and request.POST.get('action', '') == 'delete':

        # tokenizer_keyword_select 테이블에서 해당 유저의 데이터 삭제
        sql = "delete from emotions.tokenizer_keyword_select where user_id='" + request.user.username + "' or author_id='" + request.user.username + "'"
        with connection.cursor() as cursor:
            cursor.execute(sql)

        # tokenizer_user_experience 테이블에서 해당 유저의 데이터 삭제
        sql = "delete from emotions.tokenizer_user_experience where user_id='" + request.user.username + "'"
        with connection.cursor() as cursor:
            cursor.execute(sql)

        # tokenizer_user_data 테이블에서 해당 유저의 데이터 삭제
        sql = "delete from emotions.tokenizer_user_data where user_id='" + request.user.username + "'"
        with connection.cursor() as cursor:
            cursor.execute(sql)

        # auth_user 테이블에서 유저 삭제
        request.user.delete()

        return redirect('login')

    return render(request, 'tokenizer/login.html')



# login 페이지에서 forgot_password? 버튼을 눌렀을 경우
def forgot_password(request):

    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()

        # tokenizer_user_data 테이블에서 user_id와 email이 일치하는 유저가 있는지 찾아본다.
        sql = "select * from tokenizer_user_data where user_id = '" + user_id + "' and email = '" + email + "'"
        data = user_data.objects.raw(sql)
        data = serializers.serialize('json', data, ensure_ascii=False)
        data = json.loads(data)

        # 일치하는 유저가 없을 경우 다시 돌아감
        if len(data) < 1:
            error = '일치하는 계정 정보가 없습니다.'
            content = {'user_id':user_id, 'email':email, 'error':error}
            return render(request, 'tokenizer/forgot_password.html', content)
        # 일치하는 유저가 있을 경우
        else:
            content = {'user_id':user_id, 'email':email}
            return render(request, 'tokenizer/reset_password.html', content)

    return render(request, 'tokenizer/forgot_password.html')


# 비밀번호 reset
# forgot_password 페이지로부터 넘어옴
def reset_password(request):

    user_id = request.POST.get('user_id', '').strip().lower()
    email = request.POST.get('email', '').strip().lower()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    if user_id == '' or email == '':
        return render(request, 'tokenizer/reset_password.html')

    if request.method == 'POST':
        # 비밀번호 변경
        u = User.objects.get(username__exact=user_id)
        u.set_password(password1)
        u.save()
        return redirect('login')

    return render(request, 'tokenizer/reset_password.html')


def test(request):
    return render(request, 'tokenizer/test.html')