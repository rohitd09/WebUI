# Stable Diffusion Image Generator

This Node.js web application enables users to create images using the Stable Diffusion model. The project provides a simple and intuitive interface for generating images based on textual descriptions. Whether you're looking to generate art, visualize concepts, or just experiment with AI-driven image creation, this tool offers an accessible gateway into the world of AI image generation.

## Getting Started

To get the website running on your local machine, follow the steps outlined below.

### Prerequisites

1. Before you begin, ensure you have Node.js installed on your machine. If you do not have Node.js installed, follow the instructions on [Node.js official website](https://nodejs.org/) to install it.

2. Create a vitual environment

```sh
conda create -n WebUI python=3.11.*
```

3. Activate virtual environment

```sh
conda activate WebUI
```

### Installation

1. Clone the repository to your local machine:

```sh
git clone https://github.com/rohitd09/WebUI.git
cd WebUI
```

2. Install the required npm packages

```sh
npm install
```

(Optional) If you prefer to use nodemon for automatic reloading during development, install nodemon globally:

```sh
npm install nodemon -g
```

3. Install python libraries

```sh
pip install diffusers torch torchvision
```

### Running the application

To start the web application on your localhost, you can use either of the following commands:

- Using node:

```sh
node index.js
```

- Using nodemon for automatic restarts upon changes:

```sh
nodemon index.js
```

After starting the application, open your web browser and navigate to http://localhost:3000 (or the port specified in your project) to access the web interface.

### Additional Notes

1. The Stable Diffusion Pipiline is set to full precision this is necessary when using systems with NVIDIA GTX series GPUs, but if using RTX series it is efficient to switch to mixed precision by changing torch_dtype to torch.float16 from torch.float32.
2. You need to set up a new environmental variable "OPENAI_API_KEY" and set it's value to your API key.
