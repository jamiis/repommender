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
        except (ForbiddenError) as e:
            print e.__class__.__name__, e
            # if rate-limiting error
            if e.message == "API rate limit exceeded for %s." % uname:
                reset = dt.fromtimestamp(gh.rate_limit()['rate']['reset'])
                wait = (reset - dt.now()).total_seconds()
                if wait > 0:
                    sleep(wait)
            pass
        # catches all github3.exceptions
        except (GitHubError) as e:
            print e.__class__.__name__, e
            pass

# memoize star count. 
# format: { 'user/repo': star_count }
stargazers = {}

with open('data/stargazers', 'a') as f:

    since = raw_input("Continue from repo ID[None]:") or None
    for user in prevail(gh.all_users(since=since)):

        print '%s\t%s' % (user.id, user.login)

        for repo in prevail(user.starred_repositories()):

            # make another api call if stargazers count unknown
            if repo.full_name not in stargazers:
                try:
                    repo.refresh()
                    stargazers[repo.full_name] = repo.stargazers_count
                except (ForbiddenError, GitHubError, ServerError) as e:
                    print 'rep.refresh', e.__class__.__name__, e
                    continue

            f.write("%s::%s::%s::%s::%s\n" % (
                user.login,
                user.id,
                repo.full_name,
                repo.id,
                stargazers[repo.full_name]))
