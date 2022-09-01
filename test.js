const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
window = dom.window;
document = window.document;
XMLHttpRequest = window.XMLHttpRequest;
function getPathLen()
{
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute("d","M 430 360 l 380 100 l 70 10 l 98 108 l 107 99 l 95 92");
    return path
}