function loadCommentSection() {
    const commentBoardMarker = document.querySelector("comment-board");
    if (!commentBoardMarker) {
        console.error("Could not find the <comment-board> element!");
        return;
    }

    const issueNumber = commentBoardMarker.getAttribute("issue")
    if (!issueNumber) {
        console.error("The <comment-board> element does not have its `issue` attribute specified!");
        return;
    }

    const script = document.createElement("script");
    script.src = "https://utteranc.es/client.js";
    script.defer = true;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.setAttribute("repo", "ivan-resetnikov/ivan-reshetnikov.dev-db");
    script.setAttribute("issue-number", issueNumber);
    script.setAttribute("label", "utterances-discussion");
    script.setAttribute("theme", "github-dark");
    commentBoardMarker.appendChild(script);
}

loadCommentSection();
