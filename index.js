function addProjectCard(cardContainer, projectsID, metadata) {
    var roleListHTML = "";
    metadata.role_list.forEach(roleString => {
        roleListHTML += `<li>${roleString}</li>`;
    });

    var title = ``;
    if (metadata.WIP) {
        title = metadata.title;
    }
    else {
        title = `<a href="article.html?id=${projectsID}">${metadata.title}</a>`;
    }

    var card = document.createElement("div");
    card.innerHTML = `
    <div class="card">
        <div class="left">
            <div class="tip"></div>
            <img src="${metadata.preview_image_path.replace("local://", `https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/projects/${projectsID}/`)}">
            <p class="date">${metadata.date_start} - ${metadata.date_end}</p>
            <ul class="role-list">
                ${roleListHTML}
            </ul>
        </div>
        <div class="right">
            <div class="tip"></div>
            <p class="title">${title}</p>
            <p class="description">
                ${metadata.description.trim()}
            </p>
        </div>
    </div>
    `
    cardContainer.appendChild(card);
}

async function loadJSONFile(filePath) {
    try {
        const response = await fetch(filePath.replace("db://", "https://raw.githubusercontent.com/ivan-resetnikov/ivan-reshetnikov.dev-db/main/"));
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
        return null;
    }
}

async function loadProjectCards() {
    const cardContainer = document.getElementById("card-container");

    try {
        const manifest = await loadJSONFile("db://projects/manifest.json");

        for (const projectID of manifest.projectList) {
            try {
                const projectMetadata = await loadJSONFile(`db://projects/${projectID}/meta.json`);
                addProjectCard(cardContainer, projectID, projectMetadata);
            } catch (error) {
                console.error(`Could not load project '${projectID}' metadata!`);
            }
        }
    } catch (error) {
        console.error("Could not load project manifest!", error);
    }
}


loadProjectCards();

// Copy button
document.getElementById('phone-number-copy-button').addEventListener('click', () => {
    const textToCopy = "+47 405 76 305";

    navigator.clipboard.writeText(textToCopy).then(() => {
        
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
});