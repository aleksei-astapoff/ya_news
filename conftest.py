import pytest

from datetime import datetime, timedelta
from django.utils import timezone 
from news.models import Comment, News
from yanews import settings

@pytest.fixture
def client(db, client):
    return client


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def get_id_news(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def get_id_comment(comment):
    return comment.id,


@pytest.fixture
def news_list():
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
    comment.created = now + timedelta(days=index)
    comment.save()


@pytest.fixture
def form_data(author):
    return {
        'title': 'Новый заголовок',
        'author': author,
        'text': 'New text'
    }
