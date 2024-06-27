from locust import HttpUser, task, between


class UserBehavior(HttpUser):
    wait_time = between(5, 9)  # time between requests
    host = "http://127.0.0.1:5000"  # base URL

    @task
    def register_login_add_card(self):
        # Register a new user
        response = self.client.post('/register', data=dict(
            username='test_user3',
            email='test3@example.com',
            password='password',
            password2='password'
        ))

        # check registration was successful by looking at response status
        if response.status_code == 200:
            # Log in with the new user credentials
            login_response = self.client.post('/login', data=dict(
                username='test_user3',
                password='password'
            ))

            # if login was successful
            if login_response.status_code == 200:
                # add new card
                self.client.post("/cards/new", data=dict(
                    topic="Science",
                    question="What is photosynthesis?",
                    hint="Hint: It involves plants.",
                    answer="The process by which plants convert light energy into chemical energy."
                ))
