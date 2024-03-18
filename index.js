const express = require('express')
const path = require('path')
const app = express()
const port = 3000

app.use(express.urlencoded({extended: true}));
app.use(express.json())

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'))

app.get("/", (req, res) => {
    res.render("home")
});

app.post("/callPython", (req, res) => {
    const { prompt1, prompt2 } = req.body
    console.log(`The prompt for SD is "${prompt1}" and "${prompt2}"`)
    res.redirect("/")
});

app.listen(port, () => {
    console.log(`App Listening at http://localhost:${port}`);
})