# Documentation

## Project Report
<p align="left">
  <a href="https://drive.google.com/file/d/1u3mjwCqbRkNbdip-zhoenExMsZIPMzw7/view?usp=sharing" target="_blank">
    <img src="https://img.shields.io/badge/Open%20Report-blue?style=for-the-badge" alt="Report">
  </a>
</p>

## Poster
<p align="left">
  <a href="https://docs.google.com/presentation/d/1uvyCWzdRUJsl76dowc4ys9V7acRU0U-l/edit?usp=sharing&ouid=109430956441099734402&rtpof=true&sd=true" target="_blank">
    <img src="https://img.shields.io/badge/Open%20Poster-olive?style=for-the-badge" alt="Poster">
  </a>
</p>

## Poster Video
<p align="left">
  <a href="https://drive.google.com/file/d/1uf6fIy8w_ACRa2taYF162GTk6vHhomOJ/view?usp=sharing" target="_blank">
    <img src="https://img.shields.io/badge/Open%20Video-orange?style=for-the-badge" alt="Video">
  </a>
</p>

## Requirements
- Open terminal 
- Activate your venv (optional but recommended)
- Run the following command
    ```
    pip3 install flask gradio requests openai
    ```

## How to Run
- Create a .env file in your root directory
- Save two OpenAI API Keys there. 

    ```
    OPENAI_API_KEY_1 = "<YOUR_OPENAI_KEY_1>"
    OPENAI_API_KEY_2 = "<YOUR_OPENAI_KEY_2>" 
    ```

- Open a terminal in your root directory and run the following to boot up your Backend.

    ```
    python app.py
    ```
- Open another terminal in your root directory and run the following to boot up your Frontend.

    ```
    python gradio_frontend.py
    ```
      
- Open the Local/Global URL given by the gradio terminal to demo the Application.


### 💖 Developed with love by Fabian Christopher
