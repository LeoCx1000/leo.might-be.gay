import { codeToHtml, splitLines } from 'shiki';
import express from 'express';
import { readFileSync } from 'fs';

const app = express();


app.get("/hl/:file", async (req, res, next) => {
    let file = req.params.file;

    var contents = readFileSync('/www/files/' + file, 'utf8');
    var split = file.split('.');
    var html = await codeToHtml(contents, {
        lang: req.params.lang || split[split.length - 1], theme: req.query.theme || 'vitesse-dark'
    });
    res.send(html);
});

let [_, __, port] = process.argv;
app.listen(port || 39389, () => {
    console.log(`ShikiJS microservice running on port ${port || 39389}`);
});