Array.from(document.querySelectorAll(".very-lazy-img")).forEach(element => {
    const { width } = element.getBoundingClientRect(); 
    const path = element.getAttribute("path");

    const image_url = `${ path }?w=${ Math.floor(width) }`;

    element.setAttribute("src", image_url)
});
