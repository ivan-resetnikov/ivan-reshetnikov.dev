const HEAD_BOILERPLATE = `
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">

<link rel="icon" href="/images/favicon.png" type="image/png">

<link rel="stylesheet" href="/styles/generic.css">
<link rel="stylesheet" href="/styles/generic.article.css">
`

const FOOTER_HTML = `
<br>
<br>
<hr>
<p>If you're having a legal inquiry, contact me though <a href="mailto:contact@ivan-reshetnikov.dev">priority email</a>.</p>
<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://ivan-reshetnikov.dev/">ivan-reshetnikov.dev</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="mailto:legal@ivan-reshetnikov.dev">Ivan Reshetnikov</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p>
`

const TAG_DESCRIPTION_LUT = {
    "news": "Tech news",
    "playable": "Features a playable demo",
    "algorithm": "Features a unique algorithm",
}

async function renderContent(projectID, filePath, targetElement) {
    try {
        const response = await fetch(filePath.replace("db://", "https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/"));
        if (!response.ok) {
            throw new Error(`Failed to load file: ${response.statusText}`);
        }

        var markdown = await response.text();

        markdown = markdown.replaceAll("local://", `https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/projects/${projectID}/`);

        targetElement.innerHTML = marked.parse(markdown); // Render the Markdown
    } catch (error) {
        console.error(error);
        targetElement.innerHTML = '<h1 style="color:red;">Error loading content file.</h1>';
    }
}

function loadMetadata(path) {
    return fetch(path.replace("db://", "https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/"))
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            return data;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            return null;
        });
}

function generateHead(metadata) {
    // Head
    document.head.innerHTML = HEAD_BOILERPLATE;

    // Title
    const title = document.createElement("title");
    title.innerText = metadata.title;
    document.head.appendChild(title);
}


function generateFooter(main) {
    const footer = document.getElementById("footer")
    footer.innerHTML = FOOTER_HTML;
}


function generateCover(projectID, metadata) {
    const cover = document.getElementById("cover");
    cover.innerHTML = `
    <div class="page-cover" style="${metadata.cover_css.replace("local://", `https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/projects/${projectID}/`)}">
        <div class="darken-layer"></div>
        <div class="title-container">
            <p class="title" style="font-size: 64px;">${metadata.title}</p>
            <p class="sub-title">${metadata.sub_title}</p>
        </div>
    </div>
    `
}


function generateTags(main, metadata) {
    var tagContainer = document.getElementById("tags");

    var entriesHTML = "";
    metadata.tags.forEach(tagName => {
        entriesHTML += `<li><img src="../../images/project_tags/${tagName}.png" title="${TAG_DESCRIPTION_LUT[tagName]}"></li>`
    });
    
    tagContainer.innerHTML = `
    <p>Tags:</p>
    <ul class="tag-list">
        ${entriesHTML}
    </ul>
    `
}

function generateDiscussion(projectID) {
    const script = document.createElement('script');
    script.src = "https://utteranc.es/client.js";
    script.setAttribute('repo', "ivan-resetnikov/ivan-reshetnikov.dev-db");
    script.setAttribute('issue-term', projectID);
    script.setAttribute('label', "utterances-discussion");
    script.setAttribute('theme', "github-dark");
    script.crossOrigin = "anonymous";
    script.async = true;

    document.querySelector('#discussion').appendChild(script);
}


function generatePage() {
    var main = document.getElementById("main");

    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    const projectID = params.get("id");

    loadMetadata(`db://projects/${projectID}/meta.json`)
        .then(data => {
        if (data) {
            generateHead(data);
            generateCover(projectID, data);
            generateTags(main, data);
            generateFooter(main);
            generateDiscussion(projectID);

            renderContent(projectID, `db://projects/${projectID}/content.md`, document.getElementById("content"));
        } else {
            console.error("Could not load metadata!");
        }
    });
}

generatePage();
