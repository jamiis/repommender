A recommendation system for Github repositories. 

This site isn't live yet ;( I hope to finish it soon, possibly at a hackathon.
I only have 4% of github's stargazer data and will need a lot more 
in order to make up-to-date recommendations. Also, the data is still only in a
flat file so I need to get it into a db. I have tested it and it works quite 
well for the early years of github. It works for the early years because the 
scraping of github stargazer data is done in chronological order.
I would like to rotate Github API keys and get a much larger amount 
of data so the recommendations don't tend toward the first year or so 
of Github's existence.

The recommendation system algorithm used is [Implicit Collaborative Filtering](http://en.wikipedia.org/wiki/Collaborative_filtering?oldformat=true)
and I used Spark and MLlib deployed on AWS Elastic MapReduce to compute the recommendations.

For more implementation details checkout [these slides](https://jamiis.me/submodules/repommender-presentation) 
made for a presentation I gave on Repommender.
