from django.test import TestCase
from django.urls import resolve, reverse
from ..models import Board
from ..views import TopicListView

#tests for Topiclistview

class TopicListViewTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')

    def test_success_status_code_topiclistview(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_not_found_status_code_topiclistview(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_url_resolves_topiclistview(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)

    def test_contains_navigation_links_topiclistview(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))
