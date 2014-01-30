USERS = {
    1: 'admin',
    2: 'user1'
}
GROUPS = {
    1: ['g:su', 'u:1'],
    2: ['g:supervisors', 'u:2']
}


def group_finder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])