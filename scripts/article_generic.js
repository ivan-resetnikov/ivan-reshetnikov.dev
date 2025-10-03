const commentBoardMarker = document.querySelector("comment-board");

const script = document.createElement("script");
script.src = "https://utteranc.es/client.js";
script.defer = true;
script.async = true;
script.crossOrigin = "anonymous";
script.setAttribute("repo", "ivan-resetnikov/ivan-reshetnikov.dev-db");
script.setAttribute("issue-number", "3");
script.setAttribute("label", "utterances-discussion");
script.setAttribute("theme", "github-dark");
commentBoardMarker.appendChild(script);
