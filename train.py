#!/usr/bin/env python

# https://spark.apache.org/docs/1.2.0/mllib-collaborative-filtering.html

from pyspark.mllib.recommendation import ALS
from numpy import array
from pyspark import SparkContext

if __name__ == "__main__":
    sc = SparkContext(appName='TweetSentiment')

    def extract_user_repo(line, fieldtype=float):
        line = line.split('::')
        if fieldtype is float:
            # user.id, repo.id
            fields = [line[1], line[3]]
        elif fieldtype in [unicode,str]:
            # user.login, repo.full_name
            fields = [line[0], line[2]]
        return array([fieldtype(f) for f in fields])

    # load and parse the data
    data = sc.textFile("data/stargazers.sample")

    stars = data.map(extract_user_repo)
    stars.cache()

    stars_with_rating = stars.map(lambda t: array([t[0], t[1], 1]))
    stars_with_rating.cache()

    # build recommendation model using alternating least squares
    model = ALS.trainImplicit(stars_with_rating, rank=1, iterations=20)

    # evaluate the model on training data
    # testdata = ratings.map(lambda p: (int(p[0]), int(p[1])))
    predictions = model.predictAll(stars).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = stars_with_rating.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).reduce(lambda x, y: x + y)/ratesAndPreds.count()
    print("Mean Squared Error = " + str(MSE))
