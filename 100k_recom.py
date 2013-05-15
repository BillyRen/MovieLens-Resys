
from math import sqrt

#Calculate the distance-based similarity score of 2 persons
def sim_distance(prefs,person1,person2):
    #Get the list of shared items
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    
    if len(si)==0:
        return 0
    
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) 
                        for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sum_of_squares)

#Return the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,p1,p2):
    #Get the list of shared item
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
    
    if len(si)==0:
        return 0
    
    #Calculate the sum
    n=len(si)
    
    #Sum of all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p1][it] for it in si])
    
    #Sum of the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    
    #Sum of the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    
    #Calculate pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0:
        return 0
    
    r=num/den
    return r

#Return the best matches
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other)
            for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

#Return recommendations
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    
    for other in prefs:
        if other==person:
            continue
        sim=similarity(prefs,person,other)
    
        if sim<=0: 
            continue
        for item in prefs[other]:
            #Only score movies that I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
                #Similarities*Scores
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                #Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim
            
    #Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    
    #Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

#Transform the dataset
def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person]=prefs[person][item]
    return result

def calculateSimilarItems(prefs,n=10):
    result={}
    itemPrefs=transformPrefs(prefs)
    c=0;
    for item in itemPrefs:
        c+=1;
        if c%100==0:
            print "%d %d" %(c,len(itemPrefs))
        scores=topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item]=scores
    return result

def getRecommandeationItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    
    #Loop over items rated by this user
    for (item,rating) in userRatings.items():
        #Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:
            #Ignore if this item has already be rated by this user
            if item2 in userRatings:
                continue
            #Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            #Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
    
    #Divide each total score by total weighting to get average
    rankings=[(score/totalSim[item],item) 
              for item,score in scores.items()]
    
    #Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

#Load Database    
def loadMovieLens(path='C:/Users/Billy/workspace/movielens'):
    #Get the movie title
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title
    #Load data
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)
    return prefs    
        