#!/usr/bin/env python
# coding: utf-8

# In[1]:


import praw
import networkx as nx
import numpy as np
import itertools
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv


# In[2]:
load_dotenv()
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USER = os.getenv('REDDIT_USER')
REDDIT_PASS = os.getenv('REDDIT_PASS')

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_SECRET,
                     user_agent="A bot - Looks at interconnectedness of subreddits",
                     username=REDDIT_USER,
                     password=REDDIT_PASS)


# In[3]:


n_subreddits = 50
n_posts = 10000

home, *subreddits = reddit.subreddits.popular(limit=n_subreddits)


# Get `limit` most recent comments from each subreddit
# 
# Comments what were deleted for removed with have `NoneType` so we filter those out before asking for the author name.

# In[4]:


def get_flattened_comment_tree(subreddit, limit):
    
    print(f"Reading from {subreddit}")
    comments = subreddit.comments(limit=limit)
    
    author_generator = filter(None, (comment.author for comment in comments))
    return [author.name for author in author_generator]


# In[ ]:


subreddit_commentors = {subreddit.display_name: get_flattened_comment_tree(subreddit, n_posts) for subreddit in subreddits}
subreddit_unique = {name: set(commentors) for name, commentors in subreddit_commentors.items()}


# Find the relatedness of all subreddits.
# 
# For two subreddit comment sets $A$ and $B$, find the size of $\frac{A \cap B}{A}$

# In[ ]:


pairwise_subreddits = itertools.product(subreddit_unique.items(), subreddit_unique.items())

relatedness = {}

for (name1, commentors1), (name2, commentors2) in pairwise_subreddits:
    
    if name1 == name2:
        continue 
        
    intersect_size = len(commentors1.intersection(commentors2))
    name1_size = len(commentors1)
    
    
    weight = intersect_size / name1_size
    
   
    try:
        relatedness[name1][name2] = weight
        
    except KeyError:
        relatedness[name1] = {name2: weight}


# For each subreddit, find the one other subreddit which is most closely related, and draw a directed edge to that other subreddit.
# 
# The most closely related subreddit to $A$ is the subreddit where $A$ commentors most frequently post outside of $A$.
# 
# Remove edges if $weight = 0$. This preserves the nodes. 

# In[ ]:


G = nx.DiGraph()

closest_relatives = {}

for subreddit, other_subreddits in relatedness.items():
    
    closest_relative = max(other_subreddits, key=lambda x: other_subreddits[x])
    weight = other_subreddits[closest_relative]
    G.add_edge(subreddit, closest_relative, weight=weight)
    
    if weight == 0:
        G.remove_edge(subreddit, closest_relative)


# Draw stuff!

# In[ ]:


plt.figure(figsize=(24, 24))

pos = nx.spring_layout(G)
#nx.draw_networkx_nodes(G, pos, edgecolors="black", node_color="lightgrey")
nx.draw_networkx_labels(G, pos, font_weight="bold", font_size=18)
_ = nx.draw_networkx_edges(G, pos)  # save in dummy variable to hide annoying output

