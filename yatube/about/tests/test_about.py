from .conf import (TestConfig, TEST_URL_STATUS,
                   TEST_URL_TEMPLATE, TEST_VIEW_TMPLT, USER_STATUS)


class AboutURLTests(TestConfig):
    def test_about_urls(self):
        """Page's availability."""
        for page in TEST_URL_STATUS.keys():
            for user_case in USER_STATUS:
                with self.subTest():
                    response = self.clients[user_case].get(page)
                    self.assertEqual(
                        response.status_code,
                        TEST_URL_STATUS[page][USER_STATUS.index(user_case)],
                        (f'Incorrect status on the page {page} '
                         f'for {user_case}')
                    )

    def test_urls_about_uses_correct_template(self):
        """URL uses correct template."""
        for user_case in USER_STATUS:
            for address, template in TEST_URL_TEMPLATE[user_case].items():
                with self.subTest(address=address):
                    response = self.clients[user_case].get(address)
                    self.assertTemplateUsed(response, template)

    def test_pages_about_uses_correct_template(self):
        """View-function uses correct template."""
        for user_case in USER_STATUS:
            for reverse_name, tmplate in TEST_VIEW_TMPLT[user_case].items():
                with self.subTest(reverse_name=reverse_name):
                    response = self.clients[user_case].get(reverse_name)
                    self.assertTemplateUsed(
                        response,
                        tmplate,
                        ('Incorrect template for view-function '
                         f'{reverse_name} to {user_case}')
                    )
