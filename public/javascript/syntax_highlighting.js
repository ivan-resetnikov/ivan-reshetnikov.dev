function code_str_resize_indent(p_source, p_source_tab_width, p_target_tab_width) {
    const source = p_source.replace(/\t/g, ' '.repeat(p_source_tab_width));

    const lines = source.split('\n');

    const new_lines = lines.map(line => {
        const regex = new RegExp(' '.repeat(p_source_tab_width), 'g');
        return line.replace(regex, ' '.repeat(p_target_tab_width));
    });

    return new_lines.join('\n');
}


Array.from(document.querySelectorAll("pre code")).forEach(element => {
    var source = element.innerText;

    if (window.matchMedia("(max-width: 768px)").matches) {
        // NOTE(vanya): The viewport is likely of a mobile device
        source = code_str_resize_indent(source, 4, 2);
    } else {
        // NOTE(vanya): The viewport is likely of a desktop device
        source = code_str_resize_indent(source, 4, 4);
    }

    const keywords = ["await", "func", "var", "static", "class", "class_name", "extends", "signal", "if", "elif", "else", "for", "in", "is"];
    const types = ["void", "bool", "int"];
    const punctuation = [".", ",", ";", "(", ")", "[", "]", "{", "}"];

    const regex_string_split = /(".*?"|'.*?'|`.*?`)/gs;
    const regex_keywords = new RegExp(`\\b(${keywords.join("|")})\\b`, "gi");
    const regex_types = new RegExp(`\\b(${types.join("|")})\\b`, "gi");
    const regex_methods = /\b([A-Za-z0-9_]+)\(/g;
    const regex_properties = /\b\.([A-Za-z0-9_]+)/g;
    const regex_puctuation = new RegExp(`(${ punctuation.map(c => `\\${c}`).join("|") })`, "gi");

    var formatted_source = source.split(regex_string_split).map(part => {
        if (/^["'`].*["'`]$/.test(part)) {
            return `<span style="color: #369940">${part}</span>`;
        } else {
            part = part.replace(regex_keywords, `<span style="color: #302efd">$1</span>`);
            part = part.replace(regex_types, `<span style="color: #30c492">$1</span>`);
            part = part.replace(regex_methods, `<span style="color: #9f78b8">$1(</span>`);
            part = part.replace(regex_properties, `.<span style="color: #3c6d71">$1</span>`);
            part = part.replace(regex_puctuation, `<span style="color: #888888">$1</span>`);
            part = part.replace("(", `(<wbr>`);
            part = part.replace(",", `,<wbr>`);

            return part;
        }
    }).join('');

    element.innerHTML = formatted_source;
});
