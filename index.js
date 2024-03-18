const express = require('express')
const path = require('path')
const app = express()
const port = 3000

app.use(express.urlencoded({extended: true}));
app.use(express.json())

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'))

app.get("/", (req, res) => {
    const { display, image } = req.query;
    const displayBool = display === 'true';
    res.render("home", { display: displayBool, image: image })
});

app.post("/callPython", (req, res) => {
    const { prompt } = req.body
    console.log(`The prompt for SD is "${prompt}".`)
    res.redirect(`/?display=true&image=${encodeURIComponent(prompt)}`)
});

app.listen(port, () => {
    console.log(`App Listening at http://localhost:${port}`);
})