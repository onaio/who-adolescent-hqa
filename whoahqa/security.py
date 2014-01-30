USERS = {
    'admin': 'admin',
    'user1': 'user1'
}
GROUPS = {
    'admin': ['g:su', 'u:1'],
    'user1': ['g:supervisors', 'u:2']
}


def group_finder(userid, request):
    import ipdb; ipdb.set_trace()
    if userid in USERS:
        return GROUPS.get(userid, [])