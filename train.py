#!/usr/bin/env python

# https://spark.apache.org/docs/1.2.0/mllib-collaborative-filtering.html

from pyspark.mllib.recommendation import ALS
from numpy import array
from pyspark import SparkContext
import os

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

    # load and parse the data
    data = sc.textFile("data/stargazers.mini.sample")

    stars = data.map(extract_user_repo)
    stars.cache()

    # train recommendation model using alternating least squares
    stars_with_rating = stars.map(lambda t: array([t[0], t[1], 1]))
    model = ALS.trainImplicit(stars_with_rating, rank=1, iterations=20)

    # get all user->repo pairs without stars
    users = stars.map(lambda t: t[0]).distinct()
    repos = stars.map(lambda t: t[1]).distinct()
    # output format: [ (user, repo) ... ]
    unstarred = users.cartesian(repos)\
        .join(stars)\
        .filter(lambda t: t[1][0] != t[1][1])\
        .map(lambda t: (t[0], t[1][0]))

    # predictAll unstarred user-repo pairs.
    # output format: [ (user, repo, rating) ... ]
    predictions = model.predictAll(unstarred)

    # for each user, associate the 5 repos with the highest predicted rating.
    top = predictions\
        .groupByKey()\
        .map(lambda t: (t[0], sorted(t[1], key=lambda i: -i[1][1])[:5]))\
    #.map(lambda v: writeToDynamo(v))

    print top.take(4)
