#!/usr/bin/env python

# https://spark.apache.org/docs/1.2.0/mllib-collaborative-filtering.html

from pyspark.mllib.recommendation import ALS
from numpy import array
from pyspark import SparkContext
from pprint import pprint
import os, sys

def extract_user_repo(line, fieldtype=float):
    line = line.split('::')
    if fieldtype is float:
        # user.id, repo.id
        fields = [line[1], line[3]]
    elif fieldtype in [unicode,str]:
        # user.login, repo.full_name
        fields = [line[0], line[2]]
    return array([fieldtype(f) for f in fields])

if __name__ == "__main__":
    sc = SparkContext(appName='TweetSentiment')

    env = os.getenv('ENV', 'dev')
    if  env == 'dev':
        lines = sys.argv[1] if len(sys.argv) >= 2 else '100'
        text = 'data/stargazers.%sk' % lines
    elif env == 'prod':
        text = 's3n://jamis.bucket/stargazers'

    # load and parse the text file
    data = sc.textFile(text)

    starpairs = data.map(extract_user_repo)
    starpairs.cache()

    users = starpairs.map(lambda t: t[0]).distinct()

    # get 5% most popular repos
    repos = starpairs.map(lambda t: t[1]).distinct()
    sample = int(0.01 * repos.count())
    top_repos = starpairs\
        .groupBy(lambda t: t[1])\
        .sortBy(lambda t: len(t[1]), False)\
        .map(lambda t: t[0])\
        .take(sample)
    top_repos_rdd = sc.parallelize(top_repos)
    top_repos_rdd.cache()
    top_repos_bc = sc.broadcast(top_repos)
    pprint(top_repos[:5])

    starpairs_filtered = starpairs.filter(lambda t: t[1] in top_repos_bc.value)
    starpairs_filtered.cache()

    # train recommendation model using alternating least squares
    stars_with_rating = starpairs_filtered.map(lambda t: array([t[0], t[1], 1]))
    model = ALS.trainImplicit(stars_with_rating, rank=1)

    # get all user->repo pairs without stars
    users_repos = users.cartesian(top_repos_rdd).groupByKey()
    stars_grouped = starpairs_filtered.groupByKey()
    unstarred = users_repos.join(stars_grouped)\
        .map(lambda i: (i[0], set(i[1][0]) - set(i[1][1]) ))\
        .flatMap(lambda i: [ (i[0], repo) for repo in i[1] ] )

    # predict unstarred user-repo pairs.
    predictions = model.predictAll(unstarred)

    # for each user, associate the 5 repos with the highest predicted rating.
    top = predictions\
        .map(lambda t: (t[0], (t[1],t[2])))\
        .groupByKey()\
        .map(lambda t: (t[0], [i[0] for i in sorted(t[1], key=lambda i: -i[1])[:5]]))\
        .coalesce(1)

    if  env == 'dev':
        top.saveAsTextFile('data/recommendations.%sk' % lines)
    elif env == 'prod':
        text = 's3n://jamis.bucket/recommendations'
