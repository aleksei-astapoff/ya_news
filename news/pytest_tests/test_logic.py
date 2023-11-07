import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonimus_cant_post_comment(client, form_data, news):
    "Анонимный пользователь не может отправлять комметнарий"
    start_count_comment = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    finish_count_comment = Comment.objects.count()
    assert start_count_comment == finish_count_comment


@pytest.mark.django_db
def test_auth_user_can_post_comment(author_client, form_data, news):
    "Авторизованный пользователь может отправлять комметнарий"
    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == form_data['author']


def test_users_cant_use_badwords(author_client, news):
    "Пользователи не моуг использовать запрещенные слова"
    bad_text = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comment_count_first = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_text)
    assert response.context['form'].errors.get('text') == [WARNING]
    comment_count_last = Comment.objects.count()
    assert comment_count_first == comment_count_last


def test_author_can_edit_note(author, author_client,
                              news, comment, form_data):
    "Авторизованный пользователь может редактировать комментарии"
    edit_url = reverse('news:edit', args=(comment.id,))
    url = reverse('news:detail', args=(news.id,))
    url_to_comments = url + '#comments'
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_author_delete_comment(author_client, comment, news):
    "Авторизованный пользователь может удалять свои комментарии"
    start_count_comment = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    url = reverse('news:detail', args=(news.id,))
    url_to_comments = url + '#comments'
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    finish_count_comment = Comment.objects.count()
    assert finish_count_comment == start_count_comment - 1


def test_user_cant_edit_comment_of_another_user(author, admin_client,
                                                news, comment, form_data):
    "Авторизованный пользователь не может редактировать чужие комментарии"
    comment_text = comment.text
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
    assert comment.news == news
    
    assert comment.author == author


def test_user_can_delete_comment(admin_client, comment):
    "Авторизованный пользователь не может удалять чужие комментарии"
    comment_count_first = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count_last = Comment.objects.count()
    assert comment_count_first == comment_count_last
