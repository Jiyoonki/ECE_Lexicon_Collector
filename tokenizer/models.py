from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

# Create your models here.

class Tokenoutput(models.Model):
    textoutput = models.TextField

    def __str__(self):
        return self.textoutput


class keyword_select(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=100)
    user_key = models.IntegerField()
    author_id = models.CharField(max_length=100)
    pos_text = models.TextField(null=True)
    neg_text = models.TextField(null=True)
    pos_text_norm = models.TextField(null=True)
    neg_text_norm = models.TextField(null=True)
    pos_text_norm_edited = models.TextField(null=True)
    neg_text_norm_edited = models.TextField(null=True)
    pos_keyword = models.TextField(null=True)
    neg_keyword = models.TextField(null=True)
    pos_word_num = models.TextField(null=True)
    neg_word_num = models.TextField(null=True)
    rand_order = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'keyword selection'
        verbose_name_plural = 'keyword selections'

    def __str__(self):
        return self.pos_text

class keyword_visualizer(keyword_select):
    class Meta:
        proxy = True
        verbose_name = 'keyword visualizer'
        verbose_name_plural = 'keyword visualizer'

class progress_state(models.Model):

    user_id = models.CharField(max_length=100, primary_key=True)
    latest_update = models.DateTimeField(blank=True, null=True)
    cnt = models.IntegerField("total", null=True)
    max_rand_order = models.IntegerField("completed", null=True)
    progress = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'progress state'
        verbose_name_plural = 'progress states'

    def current_progress(self):
        percentage = self.progress

        return format_html(
            '''
            <progress value="{0}" max="100"></progress>
            <span style="font-weight:bold">{0}%</span>
            ''',
            percentage
        )


# user 데이터 테이블
class user_data(models.Model):
    auth_user_pk = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    birth = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    pos_text = models.TextField(null=True)
    neg_text = models.TextField(null=True)
    pos_emo1 = models.CharField(max_length=100)
    pos_emo2 = models.CharField(max_length=100)
    pos_emo3 = models.CharField(max_length=100)
    pos_emo4 = models.CharField(max_length=100)
    pos_emo5 = models.CharField(max_length=100)
    neg_emo1 = models.CharField(max_length=100)
    neg_emo2 = models.CharField(max_length=100)
    neg_emo3 = models.CharField(max_length=100)
    neg_emo4 = models.CharField(max_length=100)
    neg_emo5 = models.CharField(max_length=100)
    pos_emo1_w = models.IntegerField(null=True)
    pos_emo2_w = models.IntegerField(null=True)
    pos_emo3_w = models.IntegerField(null=True)
    pos_emo4_w = models.IntegerField(null=True)
    pos_emo5_w = models.IntegerField(null=True)
    neg_emo1_w = models.IntegerField(null=True)
    neg_emo2_w = models.IntegerField(null=True)
    neg_emo3_w = models.IntegerField(null=True)
    neg_emo4_w = models.IntegerField(null=True)
    neg_emo5_w = models.IntegerField(null=True)
    op_1 = models.IntegerField(null=True)
    op_2 = models.IntegerField(null=True)
    op_3 = models.IntegerField(null=True)
    con_1 = models.IntegerField(null=True)
    con_2 = models.IntegerField(null=True)
    con_3 = models.IntegerField(null=True)
    neuro_1 = models.IntegerField(null=True)
    neuro_2 = models.IntegerField(null=True)
    neuro_3 = models.IntegerField(null=True)
    extra_1 = models.IntegerField(null=True)
    extra_1R = models.IntegerField(null=True)
    extra_2 = models.IntegerField(null=True)
    extra_3 = models.IntegerField(null=True)
    agree_1 = models.IntegerField(null=True)
    agree_2 = models.IntegerField(null=True)
    agree_3 = models.IntegerField(null=True)
    op_avg = models.CharField(max_length=100,null=True)
    agree_avg = models.CharField(max_length=100,null=True)
    extra_avg = models.CharField(max_length=100,null=True)
    con_avg = models.CharField(max_length=100,null=True)
    neuro_avg = models.CharField(max_length=100,null=True)

# user가 입력한 경험 데이터 테이블
class user_experience(models.Model):
    auth_user_pk = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100)
    updated_date = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=100)
    user_key = models.IntegerField()
    author_id = models.CharField(max_length=100)
    pos_text = models.TextField(null=True)
    neg_text = models.TextField(null=True)
    pos_text_norm = models.TextField(null=True)
    neg_text_norm = models.TextField(null=True)