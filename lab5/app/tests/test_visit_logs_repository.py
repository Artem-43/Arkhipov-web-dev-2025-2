def test_add_and_get_all(visit_logs_repository, existing_user):
    visit_logs_repository.create('/', user_id=existing_user.id)
    visit_logs_repository.create('/users/2')
    visits = visit_logs_repository.all()
    assert any(visit['path'] == '/' and visit['user_id'] == existing_user.id for visit in visits)
    visit_logs_repository.clear_all()


def test_count_returns_correct_number(visit_logs_repository, existing_user):
    visit_logs_repository.create('/users/1', user_id=existing_user.id)
    visit_logs_repository.create('/', user_id=existing_user.id)
    visit_logs_repository.create('/')

    total = visit_logs_repository.count()
    user_total = visit_logs_repository.count(user_id=existing_user.id)

    assert total == 3
    assert user_total == 2
    visit_logs_repository.clear_all()


def test_stats_by_page(visit_logs_repository, existing_user):
    visit_logs_repository.create('/', user_id=existing_user.id)
    visit_logs_repository.create('/', user_id=existing_user.id)
    visit_logs_repository.create('/auth/login')

    stats = visit_logs_repository.stats_by_page()

    paths = [s['path'] for s in stats]
    assert '/' in paths
    assert '/auth/login' in paths

    home_visits = next(s for s in stats if s['path'] == '/')['visits']
    assert home_visits == 2
    visit_logs_repository.clear_all()


def test_stats_by_user(visit_logs_repository, existing_user):
    visit_logs_repository.create('/users/1', user_id=existing_user.id)
    visit_logs_repository.create('/users/2', user_id=existing_user.id)
    visit_logs_repository.create('/')

    stats = visit_logs_repository.stats_by_user()
    usernames = [stat['username'] for stat in stats]

    full_name = f"{existing_user.last_name} {existing_user.first_name} {existing_user.middle_name}"
    assert full_name in usernames
    assert 'Неаутентифицированный пользователь' in usernames
    visit_logs_repository.clear_all()
