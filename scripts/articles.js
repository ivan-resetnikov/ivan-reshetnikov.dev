export function populatePostList() {
    const ALL_ARTICLES = [
        {
            "name": "Software triangle rasterisation",
            "id": "005"
        },
        {
            "name": "C/C++, SDL3, and OpenGL ES on Android",
            "id": "004"
        },
        {
            "name": "PBR rendering",
            "id": "003"
        },
        {
            "name": "Voxel terrain mesh generation",
            "id": "002"
        },
        {
            "name": "Sub-Surface Scattering (SSR) Approximation",
            "id": "001"
        },
        {
            "name": "Height blended materials maps",
            "id": "000"
        }
    ];

    const postList = document.querySelector("#post-list");

    postList.innerHTML = ``;
    ALL_ARTICLES.forEach(articleData => {
        postList.innerHTML += `<li><a href="/?page=article&id=${articleData.id}">${articleData.name}</a></li>`;
    });
}

populatePostList();
