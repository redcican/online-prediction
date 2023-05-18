mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"18703812923ml@gmail.com\"\n\
" > ~/.streamlit/secrets.toml


echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml