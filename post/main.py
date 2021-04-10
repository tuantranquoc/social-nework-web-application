from load_data import data
from recommender import algo

trainingSet = data.build_full_trainset()

algo.fit(trainingSet)


prediction = algo.predict('H', 1)
print(prediction.est)

