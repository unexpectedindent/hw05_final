from http import HTTPStatus

from django.core.cache import cache

from .conf import (REDIRECTS, TestConfig, TEST_URL_STATUS,
                   TEST_URL_TEMPLATE, USER_STATUS)


class PostURLTests(TestConfig):
    def test_post_urls(self):
        """Page's availability."""
        for page in TEST_URL_STATUS.keys():
            for user_case in USER_STATUS:
                with self.subTest(page=page, user_case=user_case):
                    cache.clear()
                    response = self.clients[user_case].get(page)
                    self.assertEqual(
                        response.status_code,
                        TEST_URL_STATUS[page][USER_STATUS.index(user_case)],
                        (f'Incorrect status on the page {page} '
                         f'for {user_case}')
                    )

    def test_redirects(self):
        """Redirects."""
        for user_case in USER_STATUS:
            for page, redirect_page in REDIRECTS[user_case].items():
                with self.subTest(page=page, user_case=user_case):
                    cache.clear()
                    response = self.clients[user_case].get(
                        page,
                        follow=True
                    )
                    self.assertRedirects(
                        response, redirect_page
                    )

    def test_urls_uses_correct_template(self):
        """URL uses correct template."""
        for user_case in USER_STATUS:
            for address, template in TEST_URL_TEMPLATE[user_case].items():
                with self.subTest(address=address):
                    cache.clear()
                    response = self.clients[user_case].get(address)
                    self.assertTemplateUsed(response, template)

    def test_non_existent_dage(self):
        """Error 404 for non-existent page."""
        for user_case in USER_STATUS:
            with self.subTest(user_case=user_case):
                response = self.clients[user_case].get(
                    '/non_existent_page/'
                )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
