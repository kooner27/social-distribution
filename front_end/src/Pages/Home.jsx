import React from "react";
import { Box, Stack, Skeleton } from "@mui/material";
import Post from "../Components/post/Post";
import { useState } from "react";
import CreatePost from "../Components/createpost/CreatePost";
import Button from "@mui/material/Button";
import usePostsViewModel from "../api/PostsViewModel";

function Home() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { loading, posts } = usePostsViewModel();

  const openCreateModal = () => {
    setIsCreateModalOpen(true);
  };

  const closeCreateModal = () => {
    setIsCreateModalOpen(false);
  };

  return (
    <Box px={{ md: 22 }} sx={{ paddingTop: "10px" }}>
      {loading ? (
        <Stack
          spacing={1}
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Skeleton variant="text" height={100} width={700} />
          <Skeleton variant="text" height={20} width={700} />
          <Skeleton variant="text" height={20} width={700} />
          <Skeleton variant="rectangular" height={300} width={700} />
        </Stack>
      ) : (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Button
            onClick={openCreateModal}
            style={{
              fontSize: "1.8rem",
              color: "#adb5bd",
              textTransform: "none",
              backgroundColor: "transparent",
              boxShadow: "none",
            }}
          >
            New post +
          </Button>
          {posts.map((post, index) => {
            return <Post post={post} width="60vw" padding={1} margin={1} />;
          })}
        </Box>
      )}
      <CreatePost
        open={isCreateModalOpen}
        onClose={closeCreateModal}
        action="CREATE"
      />
    </Box>
  );
}

export default Home;
