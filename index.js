const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const session = require('express-session');
const app = express();
const port = 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: 'your secret key',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: !true } 
}));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'));

app.get("/", (req, res) => {
    const { display, image, prompt } = req.session;
    req.session.display = null;
    req.session.image = null;
    req.session.prompt = null;
    const displayBool = display === 'true';
    res.render("home", { display: displayBool, image: image, prompt: prompt });
});

app.post("/", (req, res) => {
    const { prompt } = req.body;
    console.log(`The prompt for SD is "${prompt}".`);

    const pythonProcess = spawn('python', ['diffuser.py', '--prompt', prompt]);

    let imageBase64 = '';
    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        imageBase64 += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            res.status(500).send('Error generating the image');
        } else {
            req.session.display = 'true';
            req.session.image = imageBase64.trim();
            req.session.prompt = prompt;
            res.redirect("/");
        }
    });
});

app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});
