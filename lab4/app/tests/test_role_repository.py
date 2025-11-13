def test_get_by_id_with_existing_role(role_repository, existing_role):
    role = role_repository.get_by_id(existing_role.id)
    # print(role)
    assert role['id'] == existing_role.id
    assert role['name'] == existing_role.name

def test_get_by_id_with_nonexisting_role(role_repository, nonexisting_role_id):
    role = role_repository.get_by_id(nonexisting_role_id)
    assert role is None

def test_all_with_nonempty_db(role_repository, example_roles):
    roles = role_repository.all()
    assert len(roles) == len(example_roles)
    for loaded_role, example_role in zip(roles, example_roles):
        assert loaded_role['id'] == example_role.id
        assert loaded_role['name'] == example_role.name

def test_all_roles_returns_roles_list(role_repository, example_roles):
    roles = role_repository.all()
    assert isinstance(roles, list)
    assert len(roles) == len(example_roles)
    for expected, actual in zip(example_roles, roles):
        assert expected.id == actual['id']
        assert expected.name == actual['name']

