import { useState, useEffect, useContext, useCallback } from 'react';
import axios from 'axios';
import { StoreContext } from './../store';

const usePostsViewModel = () => {
    const { state } = useContext(StoreContext);
    const userId = state.user.id;
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true)
  
    const fetchPosts = useCallback(async () => {
    try {

        // Get all authors
        const users_response = await axios.get('http://127.0.0.1:8000/api/authors/');
        const authors = users_response.data.items
        let data = []

        if (users_response.status === 200){
            for (let author of authors.slice(1)){

                // loop through authors (skipping admin) and get all posts
                const posts_response = await axios.get(`${author.url}/posts/`);

                if (posts_response.status === 200){
                    data = data.concat(posts_response.data)
                } else {
                    console.error(`cant fetch posts. status code: ${posts_response.status}`);
                }
            }

            // get ids of the authers I am following
            const following_response = await axios.get(`${userId}/following/`);
            const following = following_response.data
            let followingIds = following.map(function(item) {
                return item.user.id;
              });
            
            // filter the public posts, users posts and freinds posts
            data = data.filter(function(item) {
                return item.visibility === 'public' || item.author.id === userId || (followingIds.includes(item.author.id) && item.visibility === 'friends');
            });

            //TODO: sort by published date

            setPosts(data.reverse());
            setLoading(false)
        } else {
            console.error(`cant fetch authors. status code: ${users_response.status}`);
        }


    } catch {
        console.log('Error')
    }
    },[userId]);
  
    const createPost = async (title, description, contentType, content, visibility) => {
      const body = {
        "title": title,
        "description": description,
        "contentType": contentType,
        "content": content,
        "published": null,
        "visibility": visibility,
        "unlisted": false
      }
      const response = await axios.post(`${userId}/posts/`, body);
      
      if (response.status === 200) {
        console.error('Followed');
      } else {
        console.error('Error following author');
      }
    };

    useEffect(() => {
        fetchPosts();
    }, [fetchPosts]);

  
    return {
      loading,
      posts,
      fetchPosts,
      createPost
    };
  };
  
  export default usePostsViewModel;
  