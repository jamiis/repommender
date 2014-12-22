#!/usr/bin/env python

from datetime import datetime as dt
from getpass import getpass
from time import sleep

import github3
from github3.exceptions import ForbiddenError, GitHubError, ServerError

# authenticate with github
uname = raw_input("Github username[jamiis]:") or "jamiis"
pwd = getpass()
gh = github3.login(uname, pwd)

def sleep_on_rate_limit(err):
    '''sleep until github api requests reset'''
    # note: dumb way to check error type but there is no rate limit specific err
    if err.message == "API rate limit exceeded for %s." % uname:
        # check rate limit every 5 minute
        retry_in = 60*5
        while True:
            if gh.rate_limit()['rate']['remaining']:
                return
            print 'continue in', retry_in/60.0, 'minutes'
            sleep(retry_in)

def prevail(gen):
    '''
    forces generator to continue even on error. very naive! don't use 
    unless you really want to brute force the generator to continue.
    '''
    while True:
        try:
            yield next(gen)
        except StopIteration:
            raise
        # catches all github3.exceptions
        except GitHubError as e:
            print e.__class__.__name__, e
            sleep_on_rate_limit(e)
            pass

with open('data/stargazers', 'a') as f:

    since = raw_input("Continue from repo ID[None]:") or None
    for user in prevail(gh.all_users(since=since)):

        print '%s\t%s' % (user.id, user.login)

        for repo in prevail(user.starred_repositories()):

            f.write("%s::%s::%s::%s\n" % (
                user.login,
                user.id,
                repo.full_name,
                repo.id))
