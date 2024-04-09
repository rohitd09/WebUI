const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const session = require('express-session');
const app = express();
const port = 3000;
app.use(express.static(__dirname + "/public"));
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
    let imageData = '';

    pythonProcess.stdout.on('data', (data) => {
        imageData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        // Handle error if necessary
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            res.status(500).send('Error generating the image');
            return;
        }

        // Parse the output data
        const lines = imageData.split('\n');
        let relevantData;
        for (const line of lines) {
            // Parse the line to extract relevant data based on your protocol
            if (line.startsWith('Result:')) {
                relevantData = line.split(': ')[1].trim(); // Extracting the relevant data part
                console.log(`The result of add_text = "${relevantData}".`);
                break;
            }
        }

        if (!relevantData) {
            console.error('No relevant data found in Python output');
            res.status(500).send('Error generating the image');
            return;
        }

        // Process the relevant data as needed
        relevantData = relevantData.replaceAll("'", '"');
        let textLines = relevantData.split(']')[0].trim().split('[')[1].trim();
        relevantData = relevantData.split(']')[1].trim().split(')')[0].trim().substring(1);
        let [imgSrc, imgDes, x, y] = relevantData.trim().split(',');
        imgSrc = imgSrc.trim();
        imgDes = imgDes.trim();
        x = x.trim();
        y = y.trim();
        res.render("overlay", { textLines, imgSrc, imgDes, x, y });
    });
});



app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});
