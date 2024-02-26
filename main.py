from pymongo import MongoClient
import sys

def connect_to_db(port):
    client = MongoClient('localhost', int(port))
    return client['291db']

    
def main_menu(db):
    while True:
        print("\n1. Search Tweets\n2. Search Users\n3. List Top Tweets\n4. List Top Users\n5. Compose Tweet\n6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            search_tweets(db,"tweets")
        elif choice == "2":
            search_users(db, "tweets")
        elif choice == "3":
            list_top_tweets(db,"tweets")
        elif choice == "4":
            list_top_users(db, "tweets")
        elif choice == "5":
            compose_tweet(db, "tweets")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")



def search_tweets(db, collection_name):
    tweets_collection = db[collection_name]
    tweets_collection.create_index([("content", "text")])

    print('Please enter one or more keywords of the tweet you wanna search:')
    user_input = input()
    keywords = user_input.split()
    query = ' '.join(keywords)
    cursor = tweets_collection.find({"$text": {"$search": query}}, {"id": 1, "date": 1, "content": 1, "user.username": 1}, collation={"locale": "en", "strength": 2})
    results = []
    for tweet in cursor:
        tweet['username'] = tweet['user']['username'] if 'user' in tweet and 'username' in tweet['user'] else None
        del tweet['user']  
        results.append(tweet)
    if not results:
        print("No tweets found with the given keywords.")
        return
    else:
        for tweet in results:
            print(f"ID: {tweet['id']}, Date: {tweet['date']}, Content: '{tweet['content']}', Username: '{tweet['username']}'\n")
        while True:
            print('Enter s if you wanna see more statistics of a tweet, enter e to exit:')
            user_option = input().strip().lower()
                    
            if user_option == 's':
                get_tweet_stats(db, collection_name)
                return

            elif user_option =='e':
                return
            else:
                print('Please enter s or e')


def get_tweet_stats(db,collection_name):
    tweets_collection = db[collection_name]
    
    while True:
        print('Please enter the tweet id that you wanna view:')
        tweet_id = input()
        try:
            # Try converting the input to an integer
            tweet_id = int(tweet_id)
            tweet = tweets_collection.find_one({"id": tweet_id})
            if tweet is None:
                print('Tweet ID does not exist')
            else:
                break
        except ValueError:
            # If conversion to integer fails, print a message and continue the loop
            print("The input is not an integer. Please try again.")
    tweet_details = (
        f"Tweet_ID: {tweet['id']}\n "
        f"Username: {tweet['user']['username']}\n"
        f"Date: {tweet['date']}\n"
        f"Content: '{tweet['content']}'\n"
        f"Reply Count: {tweet['replyCount']}\n"
        f"Retweet Count: {tweet['retweetCount']}\n"
        f"Like Count: {tweet['likeCount']}\n"
        f"Quote Count: {tweet['quoteCount']}\n"
        f"URL: {tweet['url']}\n"
    )
    print('Tweet details of the tweet you selected:')
    print(tweet_details)


def list_top_tweets(db, collection_name):
    tweets_collection = db[collection_name]
    
    while True:
        field = input('Enter the field you want to rank the tweets (retweetCount, likeCount, quoteCount): ').strip()

        if field not in ['retweetCount', 'likeCount', 'quoteCount']:
            print('Invalid field. Please select from retweetCount, likeCount, or quoteCount (Case sensitive).')
        
        else:
            n = input('Enter the number of top tweets to list: ')
            try:
                n = int(n)
                break
            except ValueError:
                print('Invalid input. Please enter an integer.')
    
    top_tweets = tweets_collection.find().sort(field, -1).limit(n)

    print(f"Top {n} tweets based on {field}:")
    for tweet in top_tweets:
        print(f"Tweet_ID: {tweet['id']}, Username: '{tweet['user']['username']}', Date: {tweet['date']}, Content: '{tweet['content']}'")
    
    while True:
            print('Enter s if you wanna see more statistics of a tweet, enter e to exit:')
            user_option = input().strip().lower()
                    
            if user_option == 's':
                get_tweet_stats(db, collection_name)
                return

            elif user_option =='e':
                return
            else:
                print('Please enter s or e')

def compose_tweet(db, collection_name):
    # Compose a tweet and insert it into the database
    content = input("Enter your tweet content: ")
    collection = db[collection_name]

    # generate the tweet id
    largest_id = collection.find_one(sort=[("id", -1)], projection={"id": 1})
    new_id = largest_id['id'] + 1 if largest_id else 1
    
    tweet = {
        "url": None,
        "date": MongoClient().db.command('serverStatus')['localTime'],
        "content": content,
        "renderedContent": content,
        "id": new_id,
        "user": {
            "username": "291user",
            "displayname": None,
            "id": None,
            "description": None,
            "rawDescription": None,
            "descriptionUrls": [],
            "verified": False,
            "created": None,
            "followersCount": 0, 
            "friendsCount": 0, 
            "statusesCount": 0, 
            "favouritesCount": 0, 
            "listedCount": 0, 
            "mediaCount": 0, 
            "location": None,
            "protected": False,
            "linkUrl": None,
            "linkTcourl": None,
            "profileImageUrl": None,
            "profileBannerUrl": None,
            "url": None
        },
        "outlinks": [],
        "tcooutlinks": [],
        "replyCount": 0,
        "retweetCount": 0,
        "likeCount": 0,
        "quoteCount": 0,
        "conversationId": None,
        "lang": None,
        "source": None,
        "sourceUrl": None,
        "sourceLabel": None,
        "media": None,
        "retweetedTweet": None,
        "quotedTweet": None,
        "mentionedUsers": None
    }
    
    collection.insert_one(tweet)
    print("Tweet composed successfully.")

def search_users(db, collection_name):
    collection = db[collection_name]
    collation = {'locale': 'en', 'strength': 2}

    
    keyword = input("Enter a keyword to search for users: ")
    regex_option = f"(^|[^\\w])({keyword})\\b"
    query = {"$or": [{"user.displayname": {"$regex": regex_option, "$options": "i"}}, 
                     {"user.location": {"$regex": regex_option, "$options": "i"}}]}
    projection = {"user.username": 1, "user.displayname": 1, "user.location": 1, "_id": 0}

    results = collection.find(query, projection).collation(collation)
    displayed_users = set()
    

    found_users = False
    for result in results:
        user_info = result.get('user')
        if user_info:
            user_tuple = (user_info['username'], user_info.get('displayname'), user_info.get('location'))
            if user_tuple not in displayed_users:
                displayed_users.add(user_tuple)
                print(f"Username: {user_info['username']}, Display Name: {user_info.get('displayname', 'N/A')}, Location: {user_info.get('location', 'N/A')}")
                found_users = True

    if not found_users:
        print("No users found matching the keyword.")
    
    while True:
        print('Enter s if you wanna see more information of a user, enter e to exit:')
        user_option = input().strip().lower()
                    
        if user_option == 's':
            get_user_details(db, collection_name)
            return

        elif user_option =='e':
            return
        else:
            print('Please enter s or e')

def list_top_users(db, collection_name):
    collection = db[collection_name]

    try:
        n = int(input("Enter the number of top users to list: "))

        users = collection.find({}, {"user.username": 1, "user.displayname": 1, "user.followersCount": 1, "_id": 0}).sort("user.followersCount", -1)

        displayed_users = set() 
        count = 0
        for user in users:
            if count >= n:
                break
            username = user["user"]["username"]
            if username not in displayed_users:
                displayed_users.add(username)
                user_info = user["user"]
                print(f"Username: {user_info['username']}, Display Name: {user_info.get('displayname', 'N/A')}, Followers Count: {user_info.get('followersCount', 'N/A')}")
                count += 1
    
    except ValueError:
        print("Please enter a valid number.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    while True:
        print('Enter s if you wanna see more information of a user, enter e to exit:')
        user_option = input().strip().lower()
                    
        if user_option == 's':
            get_user_details(db, collection_name)
            return

        elif user_option =='e':
            return
        else:
            print('Please enter s or e')



def get_user_details(db, collection_name):
    collection = db[collection_name] 

    username = input("Enter the username to get details: ")

    query = {"user.username": username}
    user = collection.find_one(query)
        
    if user and 'user' in user:
        print("\nUser Information:")
        for key, value in user['user'].items():
            print(f"{key}: {value}")
    else:
        print("User not found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: program.py <port>")
        sys.exit(1)

    port = sys.argv[1]
    db = connect_to_db(port)
    main_menu(db)
