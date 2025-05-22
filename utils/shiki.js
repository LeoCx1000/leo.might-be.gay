import { codeToHtml, splitLines } from 'shiki';
import express from 'express';
import { readFileSync } from 'fs';

const app = express();


app.get("/hl", async (req, res, next) => {
    let file = req.query.path;

    var contents = readFileSync(file, 'utf8');
    var split = file.split('.');
    var html = await codeToHtml(contents, {
        lang: req.query.lang || split[split.length - 1], theme: req.query.theme || 'vitesse-dark'
    });
    res.send(html);
});

let [_, __, port] = process.argv;
app.listen(port || 39389, () => {
    console.log(`ShikiJS microservice running on port ${port || 39389}`);
});